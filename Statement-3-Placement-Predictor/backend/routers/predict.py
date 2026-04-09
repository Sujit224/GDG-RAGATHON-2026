"""
/api/predict  –  Hybrid Placement Readiness Endpoint
Returns: score, tier, reasons, confidence, what-if, feature importance, advice
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional
from services.ml_service import predict_score

router = APIRouter()


class PredictRequest(BaseModel):
    cgpa:          float        = Field(..., ge=0, le=10,  description="CGPA on a 0–10 scale")
    tech_stack:    List[str]    = Field(default_factory=list)
    projects:      int          = Field(..., ge=0, le=20,  description="Number of projects")
    internships:   int          = Field(..., ge=0, le=10,  description="Number of internships")
    communication: float        = Field(..., ge=1, le=10,  description="Communication rating 1–10")
    open_source:   int          = Field(0,   ge=0, le=1,   description="Open-source contributor flag (0/1)")

    # Legacy aliases (backward compat with old frontend)
    num_projects:   Optional[int]   = None
    num_internships:Optional[int]   = None
    opensource:     Optional[int]   = None


class WhatIfResult(BaseModel):
    plus_1_internship:      float
    plus_1_project:         float
    score_gain_internship:  float
    score_gain_project:     float


class PredictResponse(BaseModel):
    score:              float
    ml_score:           float
    rule_score:         float
    tier:               str
    reasons:            List[str]
    confidence:         str
    advice:             str
    what_if:            WhatIfResult
    feature_importance: dict
    feature_inputs:     dict


def _build_advice(tier: str, reasons: List[str], score: float) -> str:
    base = {
        "Placement Ready 🏆":    "You're strongly positioned for placements! Focus on mock interviews, DSA practice, and polishing your resume.",
        "Almost There 🎯":        "You're close! Target 1 more internship or a standout project to break into the top tier.",
        "Needs Improvement 📈":  "Work on consistent upskilling—add real-world projects, internships, and improve your communication.",
        "Work In Progress 🔧":   "Start with fundamentals: pick a strong tech stack, build 2–3 solid projects, and apply for internships ASAP.",
        "Early Stage 🌱":         "Begin your journey now—learn core CS concepts, pick one tech stack, and build your first project this month.",
    }.get(tier, "Keep improving your profile steadily.")

    # Surface top 2 reasons as quick wins
    tips = [r for r in reasons if "❌" in r or "⚠️" in r][:2]
    if tips:
        base += "\n\n**Quick wins to improve your score:**\n" + "\n".join(f"  • {t}" for t in tips)
    return base


@router.post("/predict", response_model=PredictResponse)
async def predict(req: PredictRequest):
    # Merge legacy field names
    features = {
        "cgpa":          req.cgpa,
        "projects":      req.projects if req.projects is not None else (req.num_projects or 0),
        "internships":   req.internships if req.internships is not None else (req.num_internships or 0),
        "communication": req.communication,
        "open_source":   req.open_source if req.open_source is not None else (req.opensource or 0),
        "tech_stack":    "|".join(req.tech_stack) if req.tech_stack else "",
    }

    result = predict_score(features)

    advice = _build_advice(result["tier"], result["reasons"], result["score"])

    return PredictResponse(
        score              = result["score"],
        ml_score           = result["ml_score"],
        rule_score         = result["rule_score"],
        tier               = result["tier"],
        reasons            = result["reasons"],
        confidence         = result["confidence"],
        advice             = advice,
        what_if            = WhatIfResult(**result["what_if"]),
        feature_importance = result["feature_importance"],
        feature_inputs     = result["feature_inputs"],
    )
