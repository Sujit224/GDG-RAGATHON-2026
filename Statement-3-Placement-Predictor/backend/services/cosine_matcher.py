"""
cosine_matcher.py  —  Cosine Similarity Experience Matcher
===========================================================
Pipeline:
  1. Build a TF-IDF corpus from interview experiences (company + role + skills + text)
  2. Student profile → query string from tech_stack + skills
  3. Compute cosine_similarity(student_vector, experience_vectors)
  4. Rank + return TOP-K with:
     - match_score  (0–1 cosine similarity)
     - why_recommended  (human-readable explanation)
     - summary  (condensed experience text)

Uses sklearn only (no FAISS) — stays lightweight & fast (<50 ms).
"""

import json
import os
import re
from typing import List, Dict

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ── Constants ─────────────────────────────────────────────────────────────────
EXPERIENCES_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "experiences.json")

STRONG_TECH = {
    "mern", "react", "angular", "vue", "nextjs", "next.js",
    "node", "nodejs", "express", "fastapi", "django", "flask",
    "spring", "springboot",
    "tensorflow", "pytorch", "keras", "machine learning", "deep learning", "nlp",
    "aws", "gcp", "azure", "kubernetes", "docker", "devops",
    "go", "golang", "rust", "scala", "kotlin",
}

ROLE_KEYWORDS = {
    "sde": ["java", "c++", "dsa", "algorithms", "data structures", "system design"],
    "frontend": ["react", "vue", "angular", "css", "javascript", "typescript", "html"],
    "backend": ["python", "java", "node", "django", "fastapi", "sql", "rest api"],
    "ml": ["python", "tensorflow", "pytorch", "sklearn", "data", "model", "pandas", "numpy"],
    "devops": ["docker", "kubernetes", "aws", "ci/cd", "jenkins", "terraform"],
    "fullstack": ["react", "node", "sql", "mongodb", "api"],
}

# ── State (loaded once) ────────────────────────────────────────────────────────
_experiences: List[Dict] = []
_vectorizer: TfidfVectorizer = None
_experience_matrix = None


def _load_experiences() -> List[Dict]:
    """Load experiences from JSON file, enriching company/role from Metadata lines."""
    global _experiences
    if _experiences:
        return _experiences

    exp_path = os.path.normpath(EXPERIENCES_PATH)
    if not os.path.exists(exp_path):
        return []

    with open(exp_path, "r", encoding="utf-8") as f:
        _experiences = json.load(f)

    # Post-process: extract company/role from "Metadata: Company | Role | ..." in text
    for exp in _experiences:
        text = exp.get("text", "")
        meta = re.search(r"Metadata:\s*([^|\n]+)\|([^|\n]+)", text)
        if meta:
            company = meta.group(1).strip()
            role    = meta.group(2).strip()
            if company and (exp.get("company", "Unknown") == "Unknown"):
                exp["company"] = company
            if role and not exp.get("role"):
                exp["role"] = role
        if not exp.get("role"):
            exp["role"] = "Software Engineer"

    return _experiences


def _build_experience_document(exp: Dict) -> str:
    """
    Convert an experience dict to a rich text document for vectorization.
    Weights important fields by repetition.
    """
    parts = []

    # Company and role repeated for higher weight
    company = exp.get("company", "")
    role    = exp.get("role", exp.get("text", "")[:30])
    parts.extend([company] * 2)
    parts.extend([role] * 2)

    # Tech stack (if structured)
    tech = exp.get("tech_stack", exp.get("skills", []))
    if isinstance(tech, list):
        parts.extend(tech * 3)  # triple weight for skills
    elif isinstance(tech, str):
        parts.extend(tech.split() * 2)

    # Full text
    text = exp.get("text", exp.get("raw_chunk", ""))
    parts.append(text[:500])  # cap to 500 chars for speed

    return " ".join(str(p) for p in parts if p).lower()


def _build_student_query(tech_stack: List[str], extra_context: str = "") -> str:
    """
    Build a query string from the student's tech stack.
    Strong tech gets higher repetition weight.
    """
    tokens = []
    for tech in tech_stack:
        tl = tech.lower()
        weight = 4 if tl in STRONG_TECH else 2
        tokens.extend([tl] * weight)

    # Add extra context (e.g. more keywords from profile)
    if extra_context:
        tokens.extend(extra_context.lower().split())

    # Infer likely roles
    tl_set = {t.lower() for t in tech_stack}
    for role, keywords in ROLE_KEYWORDS.items():
        overlap = len(tl_set & set(keywords))
        if overlap >= 2:
            tokens.extend([role] * 2)

    return " ".join(tokens) if tokens else "software engineering"


def _init_vectorizer(experiences: List[Dict]):
    """Build TF-IDF matrix from all experiences (lazy load)."""
    global _vectorizer, _experience_matrix

    if _vectorizer is not None and _experience_matrix is not None:
        return

    docs = [_build_experience_document(e) for e in experiences]
    if not docs:
        return

    _vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=5000,
        stop_words="english",
        min_df=1,
        sublinear_tf=True,
    )
    _experience_matrix = _vectorizer.fit_transform(docs)


def _generate_why_recommended(exp: Dict, tech_stack: List[str], match_score: float) -> str:
    """Generate a human-readable explanation for why this experience was matched."""
    company = exp.get("company", "this company")
    role    = exp.get("role", "Software Engineer")
    exp_text = exp.get("text", "").lower()

    tech_lower = {t.lower() for t in tech_stack}
    exp_tech   = {t.lower() for t in exp.get("tech_stack", [])}

    # Find overlap
    overlap = tech_lower & exp_tech
    if not overlap:
        # Try finding tech keywords in text
        for t in tech_stack:
            if t.lower() in exp_text:
                overlap.add(t)

    reasons = []

    if overlap:
        tech_list = ", ".join(t.title() for t in list(overlap)[:3])
        reasons.append(f"Shared skills in {tech_list}")

    if match_score >= 0.75:
        reasons.append("very high overall profile alignment")
    elif match_score >= 0.5:
        reasons.append("strong skill set overlap")
    elif match_score >= 0.3:
        reasons.append("moderate experience relevance")
    else:
        reasons.append("general domain alignment")

    # Role-specific tips
    role_lower = role.lower()
    if "sde" in role_lower or "software" in role_lower:
        reasons.append("DSA and system design focus matches SDE interviews")
    elif "ml" in role_lower or "data" in role_lower:
        reasons.append("ML/AI experience pattern found")
    elif "frontend" in role_lower:
        reasons.append("frontend tech stack match")
    elif "backend" in role_lower:
        reasons.append("backend service skills aligned")

    return f"{company} ({role}): " + "; ".join(reasons) + "."


def _summarize_experience(text: str, max_chars: int = 200) -> str:
    """Create a concise summary of experience text."""
    if not text:
        return "Interview experience not available."

    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Find the most interesting sentence (contains keywords)
    sentences = re.split(r'[.!?]\s+', text)
    key_sentences = [s for s in sentences if any(
        kw in s.lower() for kw in ["asked", "round", "dsa", "system", "design", "lc", "leetcode", "hr", "technical"]
    )]
    if key_sentences:
        text = ". ".join(key_sentences[:2])

    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"

    return text


# ── PUBLIC API ─────────────────────────────────────────────────────────────────

def match_experiences(
    tech_stack: List[str],
    profile: Dict = None,
    top_k: int = 3,
) -> List[Dict]:
    """
    Match student profile against interview experiences via cosine similarity.

    Args:
        tech_stack: List of technologies the student knows
        profile: Full student profile dict (optional, for richer matching)
        top_k: Number of top matches to return

    Returns:
        List of dicts:
        {
          "company": str,
          "role": str,
          "match_score": float (0–1),
          "why_recommended": str,
          "summary": str
        }
    """
    experiences = _load_experiences()
    if not experiences:
        return []

    _init_vectorizer(experiences)

    if _vectorizer is None or _experience_matrix is None:
        return []

    # Build query
    extra = ""
    if profile:
        if profile.get("cgpa", 0) >= 8.5:
            extra += " high academic achiever top university"
        if profile.get("internships", 0) >= 2:
            extra += " experienced industry internship"
        if profile.get("open_source", 0):
            extra += " open source contributor github"

    query = _build_student_query(tech_stack, extra)
    query_vec = _vectorizer.transform([query])

    # Cosine similarity
    sims = cosine_similarity(query_vec, _experience_matrix).flatten()

    # Get top-k sorted indices
    top_indices = np.argsort(sims)[::-1][:top_k]

    results = []
    for idx in top_indices:
        exp = experiences[idx]
        raw_score = float(sims[idx])
        match_score = round(raw_score, 4)

        company = exp.get("company", "Unknown Company")
        role    = exp.get("role", "Software Engineer")
        text    = exp.get("text", exp.get("raw_chunk", ""))

        results.append({
            "company":          company,
            "role":             role,
            "match_score":      match_score,
            "why_recommended":  _generate_why_recommended(exp, tech_stack, raw_score),
            "summary":          _summarize_experience(text),
            "tech_stack":       exp.get("tech_stack", []),
        })

    return results


def reset_cache():
    """Force reload of vectorizer (useful if experiences.json is updated)."""
    global _experiences, _vectorizer, _experience_matrix
    _experiences       = []
    _vectorizer        = None
    _experience_matrix = None
