from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.ml_service import predict_score

router = APIRouter()

class PredictRequest(BaseModel):
    cgpa: float
    tech_stack: List[str]
    num_projects: int
    num_internships: int
    communication: float
    opensource: int

@router.post("/predict")
async def predict(req: PredictRequest):
    features = {
        "cgpa": req.cgpa,
        "num_projects": req.num_projects,
        "num_internships": req.num_internships,
        "communication": req.communication,
        "opensource": req.opensource,
        "tech_stack_score": min(len(req.tech_stack) / 2.0, 5.0)
    }
    score = predict_score(features)
    
    # Generate tier label and advice
    if score >= 80:
        tier = "Placement Ready"
        advice = "You're well-positioned! Focus on mock interviews and DSA."
    elif score >= 60:
        tier = "Almost There"
        advice = "Strengthen your projects and communication. 1-2 more months of prep."
    elif score >= 40:
        tier = "Needs Improvement"
        advice = "Focus on increasing CGPA, adding projects, and contributing to open source."
    else:
        tier = "Early Stage"
        advice = "Start with fundamentals: pick a core tech stack and build 2-3 solid projects."
    
    return {"score": score, "tier": tier, "advice": advice}
