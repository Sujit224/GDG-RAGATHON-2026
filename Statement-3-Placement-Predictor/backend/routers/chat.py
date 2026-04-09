"""
/api/chat — Conversational profile builder with full pipeline completion.

Flow:
  1. Forward message to LLM mentor for next question
  2. When PROFILE_COMPLETE detected:
     a. Extract structured JSON from conversation
     b. Run full hybrid ML prediction
     c. Return profile + full prediction result in one response
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from services.llm_service import chat_with_student, extract_profile
from services.ml_service import predict_score

router = APIRouter()


class ChatRequest(BaseModel):
    messages: list[dict]   # [{role: "user"/"assistant", content: "..."}]

class WhatIfResult(BaseModel):
    plus_1_internship:      float
    plus_1_project:         float
    score_gain_internship:  float
    score_gain_project:     float

class PredictionResult(BaseModel):
    score:              float
    ml_score:           float
    rule_score:         float
    tier:               str
    reasons:            List[str]
    confidence:         str
    advice:             str
    what_if:            WhatIfResult
    feature_importance: Dict[str, float]
    improvements:       List[str]

class ChatResponse(BaseModel):
    reply:            str
    profile_complete: bool
    profile:          Optional[Dict[str, Any]] = None
    prediction:       Optional[PredictionResult] = None


def _build_advice(tier: str, reasons: List[str], score: float) -> str:
    base = {
        "Placement Ready 🏆":   "You're strongly positioned for placements! Focus on mock interviews, DSA practice, and polishing your resume.",
        "Almost There 🎯":       "You're close! Target 1 more internship or a standout project to break into the top tier.",
        "Needs Improvement 📈": "Work on consistent upskilling — add real-world projects, internships, and improve your communication.",
        "Work In Progress 🔧":  "Start with fundamentals: pick a strong tech stack, build 2–3 solid projects, and apply for internships ASAP.",
        "Early Stage 🌱":        "Begin your journey now — learn core CS concepts, pick one tech stack, and build your first project this month.",
    }.get(tier, "Keep improving your profile steadily.")
    tips = [r for r in reasons if "❌" in r or "⚠️" in r][:2]
    if tips:
        base += "\n\n**Quick wins:**\n" + "\n".join(f"• {t}" for t in tips)
    return base


def _build_improvements(reasons: List[str], score: float) -> List[str]:
    """Generate actionable improvement suggestions based on what hurt the score."""
    improvements = []
    reason_text = " ".join(reasons).lower()

    if "no internship" in reason_text or "❌ no internship" in reason_text.lower():
        improvements.append("Apply for at least 1 internship — this single change can boost your score by 10–16 points")
    if "no projects" in reason_text or "❌ no projects" in reason_text.lower():
        improvements.append("Build 2–3 solid projects using a strong tech stack (MERN, Django, AI/ML)")
    if "low cgpa" in reason_text or "below 6" in reason_text:
        improvements.append("Work on improving CGPA above 6.5 to remove the hard score cap")
    if "poor communication" in reason_text or "⚠️ poor comm" in reason_text.lower():
        improvements.append("Join a public speaking club or practice mock interviews to improve communication")
    if "no recogni" in reason_text or "no tech stack" in reason_text:
        improvements.append("Learn an in-demand stack: MERN, FastAPI/Django, or AI/ML fundamentals")
    if "open-source" not in reason_text and "open source" not in reason_text:
        improvements.append("Contribute to open-source on GitHub — even 2–3 PRs add a meaningful bonus")
    if "only 1 project" in reason_text or "1 internship" in reason_text:
        improvements.append("Try to get a second internship or build 1–2 more substantial projects")

    if not improvements:
        if score >= 80:
            improvements = [
                "Prepare for DSA and system design interviews",
                "Polish your LinkedIn and GitHub profiles",
                "Apply to FAANG and top product companies",
            ]
        else:
            improvements = [
                "Build projects in a strong tech domain (AI/ML, full-stack, DevOps)",
                "Apply for internships on LinkedIn, Internshala, or AngelList",
                "Rate your communication honestly and work on mock interviews",
            ]

    return improvements[:4]


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = chat_with_student(req.messages)
    is_complete = "PROFILE_COMPLETE" in reply

    if is_complete:
        reply = reply.replace("PROFILE_COMPLETE", "").strip()

    profile = None
    prediction = None

    if is_complete:
        # STEP 1: Extract structured profile from conversation
        raw_profile = extract_profile(
            req.messages + [{"role": "assistant", "content": reply}]
        )

        # Normalise field names (LLM service uses num_/opensource; ml_service uses direct names)
        profile = {
            "cgpa":          raw_profile.get("cgpa", 7.0),
            "tech_stack":    raw_profile.get("tech_stack", []),
            "projects":      raw_profile.get("num_projects", raw_profile.get("projects", 0)),
            "internships":   raw_profile.get("num_internships", raw_profile.get("internships", 0)),
            "communication": raw_profile.get("communication", 5.0),
            "open_source":   int(bool(raw_profile.get("opensource", raw_profile.get("open_source", 0)))),
            # keep legacy keys too so ProfileExtracted component still works
            "num_projects":   raw_profile.get("num_projects", raw_profile.get("projects", 0)),
            "num_internships":raw_profile.get("num_internships", raw_profile.get("internships", 0)),
            "opensource":     raw_profile.get("opensource", 0),
        }

        # STEP 2: Feature processing + ML prediction + Domain logic → full hybrid score
        result = predict_score({
            "cgpa":          profile["cgpa"],
            "projects":      profile["projects"],
            "internships":   profile["internships"],
            "communication": profile["communication"],
            "open_source":   profile["open_source"],
            "tech_stack":    profile["tech_stack"],
        })

        # STEP 3: Build explainability & improvements
        advice       = _build_advice(result["tier"], result["reasons"], result["score"])
        improvements = _build_improvements(result["reasons"], result["score"])

        prediction = PredictionResult(
            score              = result["score"],
            ml_score           = result["ml_score"],
            rule_score         = result["rule_score"],
            tier               = result["tier"],
            reasons            = result["reasons"],
            confidence         = result["confidence"],
            advice             = advice,
            what_if            = WhatIfResult(**result["what_if"]),
            feature_importance = result.get("feature_importance", {}),
            improvements       = improvements,
        )

    return ChatResponse(
        reply            = reply,
        profile_complete = is_complete,
        profile          = profile,
        prediction       = prediction,
    )
