from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List


def _fallback_interviews() -> List[str]:
    fallback_path = Path("data/interviews.json")
    if not fallback_path.exists():
        return []
    try:
        with fallback_path.open("r", encoding="utf-8") as f:
            items = json.load(f)
        return [str(x) for x in items if str(x).strip()]
    except Exception:
        return []


def _normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-zA-Z0-9+ ]", " ", text.lower()).split())


def _dedupe_keep_order(items: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for item in items:
        key = _normalize(item)[:220]
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def get_interviews(profile):
    """
    Best-effort retrieval.

    If optional RAG deps/models aren't available (common on fresh Windows setups),
    we return an empty list so /predict and /upload-resume still work.
    """
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except Exception:
        return _fallback_interviews()[:3]

    if not Path("db").exists():
        return _fallback_interviews()[:3]

    try:
        db = Chroma(
            persist_directory="db",
            embedding_function=HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"),
        )
    except Exception:
        # e.g. sentence_transformers missing, model download blocked, etc.
        return _fallback_interviews()[:3]

    skills = (profile or {}).get("skills", []) or []
    query_parts: List[str] = list(skills)

    # Include profile signals for better semantic match
    if profile.get("projects", 0) >= 3:
        query_parts.append("projects")
    if profile.get("dsa", 0) >= 7:
        query_parts.append("dsa algorithms")
    if profile.get("experience", 0) >= 1:
        query_parts.append("internship experience")

    # Create query from skills + profile signals
    query = " ".join(query_parts)
    if not query.strip():
        return []

    # Search top candidates
    try:
        if hasattr(db, "similarity_search_with_relevance_scores"):
            pairs = db.similarity_search_with_relevance_scores(query, k=12)
            docs = [doc for doc, _ in pairs]
            semantic = {id(doc): float(score) for doc, score in pairs}
        else:
            docs = db.similarity_search(query, k=12)
            semantic = {}
    except Exception:
        return _fallback_interviews()[:3]

    skill_terms = {str(s).lower() for s in skills}
    is_ml_profile = any(s in {"ML", "AI", "NLP", "Tensorflow", "Pytorch"} for s in skills)
    ranked = []
    for doc in docs:
        content = str(doc.page_content)
        text_n = _normalize(content)

        # 1) Semantic retrieval score from vector DB (if available)
        sem_score = semantic.get(id(doc), 0.0)

        # 2) Skill overlap and exact phrase hits
        overlap = sum(1 for term in skill_terms if term.lower() in text_n)
        exact_hits = sum(2 for term in skill_terms if f" {term.lower()} " in f" {text_n} ")

        # 3) Profile-intent boosts to improve precision
        dsa_boost = 1.5 if profile.get("dsa", 0) >= 7 and ("dsa" in text_n or "algorithm" in text_n) else 0.0
        exp_boost = 1.0 if profile.get("experience", 0) >= 1 and ("intern" in text_n or "experience" in text_n) else 0.0
        proj_boost = 1.0 if profile.get("projects", 0) >= 3 and ("project" in text_n or "design" in text_n) else 0.0
        ml_boost = 1.2 if is_ml_profile and any(x in text_n for x in ["ml", "ai", "model", "nlp"]) else 0.0
        sde_boost = 1.2 if not is_ml_profile and any(x in text_n for x in ["system design", "backend", "dsa", "oop"]) else 0.0

        final_score = (
            3.0 * sem_score
            + 1.5 * overlap
            + 1.0 * exact_hits
            + dsa_boost
            + exp_boost
            + proj_boost
            + ml_boost
            + sde_boost
        )
        ranked.append((final_score, content))

    ranked.sort(key=lambda x: x[0], reverse=True)
    ordered = [text for _, text in ranked]
    top3 = _dedupe_keep_order(ordered)[:3]
    if top3:
        return top3
    return _fallback_interviews()[:3]