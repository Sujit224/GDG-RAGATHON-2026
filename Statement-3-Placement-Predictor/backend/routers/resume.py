"""
routers/resume.py  —  Resume Pipeline Endpoints
================================================
Endpoints:
  POST /upload_resume  — Upload PDF/DOCX → parse → predict → match → full JSON
  POST /extract        — Upload PDF/DOCX → return parsed profile JSON only
  POST /match          — POST JSON profile → return top-K cosine matches
"""

import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

from services.resume_parser import parse_resume
from services.ml_service import predict_score
from services.cosine_matcher import match_experiences

router = APIRouter()

# ── Shared models ─────────────────────────────────────────────────────────────

class ProfileInput(BaseModel):
    cgpa:          float       = Field(7.0,  ge=0, le=10)
    projects:      int         = Field(0,    ge=0, le=20)
    internships:   int         = Field(0,    ge=0, le=10)
    communication: float       = Field(6.0,  ge=1, le=10)
    open_source:   int         = Field(0,    ge=0, le=1)
    tech_stack:    List[str]   = Field(default_factory=list)
    top_k:         int         = Field(3,    ge=1, le=10)


class ExperienceMatch(BaseModel):
    company:          str
    role:             str
    match_score:      float
    why_recommended:  str
    summary:          str
    tech_stack:       List[str] = []


class FullPredictResponse(BaseModel):
    profile:                  Dict[str, Any]
    score:                    float
    level:                    str   # "Low" | "Medium" | "High"
    tier:                     str
    ml_score:                 float
    rule_score:               float
    confidence:               str
    reasons:                  List[str]
    improvements:             List[str]
    advice:                   str
    what_if:                  Dict[str, float]
    recommended_experiences:  List[ExperienceMatch]


# ── Helpers ───────────────────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}
MAX_FILE_SIZE_MB   = 10


def _validate_file(filename: str, size: int):
    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Upload a PDF or DOCX resume."
        )
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max {MAX_FILE_SIZE_MB}MB allowed."
        )


def _score_to_level(score: float) -> str:
    if score >= 70:
        return "High"
    elif score >= 45:
        return "Medium"
    return "Low"


def _build_improvements(reasons: List[str], score: float) -> List[str]:
    improvements = []
    reason_text = " ".join(reasons).lower()

    if "no internship" in reason_text or "❌ no internship" in reason_text:
        improvements.append(
            "Apply for at least 1 internship — can boost your score by 10–16 points"
        )
    if "no projects" in reason_text or "❌ no projects" in reason_text:
        improvements.append("Build 2–3 solid projects using MERN, Django, or AI/ML")
    if "low cgpa" in reason_text or "below 6" in reason_text:
        improvements.append("Improve CGPA above 6.5 to remove the hard score cap")
    if "poor communication" in reason_text or "⚠️ poor comm" in reason_text.lower():
        improvements.append("Practice mock interviews and improve communication skills")
    if "no recogni" in reason_text or "no tech stack" in reason_text:
        improvements.append("Learn an in-demand stack: MERN, FastAPI, or AI/ML fundamentals")
    if "open-source" not in reason_text and "open source" not in reason_text:
        improvements.append("Contribute to open-source on GitHub — even 2–3 PRs add value")
    if "only 1 project" in reason_text:
        improvements.append("Build 2 more substantial projects to strengthen your portfolio")

    if not improvements:
        if score >= 80:
            improvements = [
                "Practice DSA and system design interview problems",
                "Polish your LinkedIn and GitHub profiles",
                "Apply to top product companies",
            ]
        else:
            improvements = [
                "Build projects in a strong tech domain (AI/ML, full-stack, DevOps)",
                "Apply for internships on LinkedIn, Internshala, or AngelList",
                "Work on communication and interview skills",
            ]
    return improvements[:4]


def _build_advice(tier: str, reasons: List[str], score: float) -> str:
    base = {
        "Placement Ready 🏆":   "You're strongly positioned for placements! Focus on mock interviews, DSA practice, and polishing your resume.",
        "Almost There 🎯":       "You're close! Target 1 more internship or a standout project to break into the top tier.",
        "Needs Improvement 📈": "Work on upskilling — add real-world projects, internships, and improve your communication.",
        "Work In Progress 🔧":  "Start with fundamentals: pick a strong tech stack, build 2–3 solid projects, and apply for internships ASAP.",
        "Early Stage 🌱":        "Begin your journey — learn core CS concepts, pick one tech stack, and build your first project this month.",
    }.get(tier, "Keep improving your profile steadily.")

    tips = [r for r in reasons if "❌" in r or "⚠️" in r][:2]
    if tips:
        base += "\n\n**Quick wins:**\n" + "\n".join(f"• {t}" for t in tips)
    return base


def _run_full_pipeline(profile: dict, top_k: int = 3) -> dict:
    """
    Run: Feature Engineering → Hybrid ML Prediction → Cosine Similarity Matching
    Returns the complete standardized output JSON.
    """
    # ── STEP 1: Normalize profile ──
    tech_stack_str = profile.get("tech_stack", [])
    if isinstance(tech_stack_str, list):
        tech_list = tech_stack_str
    else:
        tech_list = [t.strip() for t in str(tech_stack_str).split("|") if t.strip()]

    features = {
        "cgpa":          float(profile.get("cgpa", 7.0)),
        "projects":      int(profile.get("projects", 0)),
        "internships":   int(profile.get("internships", 0)),
        "communication": float(profile.get("communication", 6.0)),
        "open_source":   int(profile.get("open_source", 0)),
        "tech_stack":    tech_list,
    }

    # ── STEP 2: Hybrid ML Prediction ──
    prediction = predict_score(features)

    # ── STEP 3: Build explainability ──
    score       = prediction["score"]
    tier        = prediction["tier"]
    reasons     = prediction["reasons"]
    improvements = _build_improvements(reasons, score)
    advice      = _build_advice(tier, reasons, score)

    # ── STEP 4: Cosine Similarity Matching ──
    matched = match_experiences(
        tech_stack=tech_list,
        profile=features,
        top_k=top_k,
    )

    # ── STEP 5: Assemble final response ──
    return {
        "profile": {
            "cgpa":          features["cgpa"],
            "projects":      features["projects"],
            "internships":   features["internships"],
            "communication": features["communication"],
            "open_source":   features["open_source"],
            "tech_stack":    tech_list,
        },
        "score":                 score,
        "level":                 _score_to_level(score),
        "tier":                  tier,
        "ml_score":              prediction["ml_score"],
        "rule_score":            prediction["rule_score"],
        "confidence":            prediction["confidence"],
        "reasons":               reasons,
        "improvements":          improvements,
        "advice":                advice,
        "what_if":               prediction["what_if"],
        "feature_importance":    prediction.get("feature_importance", {}),
        "recommended_experiences": [
            {
                "company":         m["company"],
                "role":            m["role"],
                "match_score":     m["match_score"],
                "why_recommended": m["why_recommended"],
                "summary":         m["summary"],
                "tech_stack":      m.get("tech_stack", []),
            }
            for m in matched
        ],
    }


# ── ENDPOINTS ──────────────────────────────────────────────────────────────────

@router.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),
    top_k: int = 3,
):
    """
    FULL PIPELINE: Upload a PDF/DOCX resume →
      Parse → Feature Engineering → Hybrid ML Prediction → Cosine Similarity → Full JSON.
    """
    content = await file.read()
    _validate_file(file.filename, len(content))

    try:
        parsed_profile = parse_resume(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing error: {e}")

    result = _run_full_pipeline(parsed_profile, top_k=top_k)
    return JSONResponse(content=result)


@router.post("/extract")
async def extract_profile(
    file: UploadFile = File(...),
):
    """
    PARSE ONLY: Upload resume → return structured profile JSON (no prediction).
    Useful for previewing parsed fields before running prediction.
    """
    content = await file.read()
    _validate_file(file.filename, len(content))

    try:
        parsed_profile = parse_resume(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing error: {e}")

    return JSONResponse(content={
        "profile": {
            "cgpa":          parsed_profile["cgpa"],
            "projects":      parsed_profile["projects"],
            "internships":   parsed_profile["internships"],
            "communication": parsed_profile["communication"],
            "open_source":   parsed_profile["open_source"],
            "tech_stack":    parsed_profile["tech_stack"],
        },
        "raw_text_length": parsed_profile["raw_text_length"],
        "filename":         file.filename,
    })


@router.post("/match")
async def match(req: ProfileInput):
    """
    COSINE MATCH ONLY: POST a profile JSON → top-K matched interview experiences
    via cosine similarity on TF-IDF vectors.
    """
    tech_list = req.tech_stack

    matched = match_experiences(
        tech_stack=tech_list,
        profile=req.dict(),
        top_k=req.top_k,
    )

    return {
        "tech_stack":    tech_list,
        "total_matched": len(matched),
        "experiences":   matched,
    }


@router.post("/analyze")
async def analyze_profile(req: ProfileInput):
    """
    PREDICT + MATCH: POST a profile JSON → full pipeline output
    (same as /upload_resume but for manually entered profiles).
    """
    result = _run_full_pipeline(req.dict(), top_k=req.top_k)
    return JSONResponse(content=result)
