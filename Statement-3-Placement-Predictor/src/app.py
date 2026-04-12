"""
Placement Predictor & Mentor - FastAPI Backend
================================================
Endpoints:
  POST /predict           - Predict readiness score from 7 features
  POST /extract-profile   - LLM extracts structured profile from chat text
  POST /chat              - Guided conversational profiling
  POST /upload-resume     - Parse resume PDF/DOCX and extract profile
  POST /match-experiences - Find top matching interview experiences
  GET  /health            - Health check
"""

import os
import json
import joblib
import numpy as np
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# ── Load environment ───────────────────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import google.generativeai as genai

GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
if GOOGLE_API_KEY and GOOGLE_API_KEY != "your_google_api_key_here":
    genai.configure(api_key=GOOGLE_API_KEY)

# ── App setup ──────────────────────────────────────────────────────────
app = FastAPI(title="Placement Predictor & Mentor API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load trained model & scaler ────────────────────────────────────────
MODEL_DIR = Path(__file__).parent / "model"
model = joblib.load(MODEL_DIR / "readiness_model.pkl")
scaler = joblib.load(MODEL_DIR / "scaler.pkl")

with open(MODEL_DIR / "metrics.json") as f:
    model_metrics = json.load(f)

FEATURE_ORDER = [
    "Academic_Score",
    "DSA_Skill",
    "Project_Quality",
    "Experience_Score",
    "OpenSource_Value",
    "Soft_Skills",
    "Tech_Stack_Score",
]

# ── ChromaDB setup ─────────────────────────────────────────────────────
import chromadb

CHROMA_DIR = Path(__file__).parent / "chroma_db"
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

try:
    experience_collection = chroma_client.get_collection("interview_experiences")
except Exception:
    experience_collection = chroma_client.get_or_create_collection("interview_experiences")


# ══════════════════════════════════════════════════════════════════════
#  SCHEMAS
# ══════════════════════════════════════════════════════════════════════

class PredictRequest(BaseModel):
    academic_score: float = Field(..., ge=0, le=10, description="CGPA (0-10)")
    dsa_skill: int = Field(..., ge=1, le=10, description="DSA proficiency (1-10)")
    project_quality: int = Field(..., ge=1, le=10, description="Project quality (1-10)")
    experience_score: int = Field(..., ge=0, le=10, description="Internship/experience (0-10)")
    opensource_value: int = Field(..., description="Open source contributions (1 or 10)")
    soft_skills: int = Field(..., ge=1, le=10, description="Communication/soft skills (1-10)")
    tech_stack_score: int = Field(..., ge=1, le=10, description="Tech stack breadth (1-10)")


class ChatMessage(BaseModel):
    message: str
    history: list = Field(default_factory=list)


class ExtractRequest(BaseModel):
    text: str


# ══════════════════════════════════════════════════════════════════════
#  ENDPOINTS
# ══════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_metrics": model_metrics,
        "experience_count": experience_collection.count(),
    }


@app.post("/predict")
async def predict_readiness(req: PredictRequest):
    """Predict readiness score from 7 profile features."""
    features = np.array([[
        req.academic_score,
        req.dsa_skill,
        req.project_quality,
        req.experience_score,
        req.opensource_value,
        req.soft_skills,
        req.tech_stack_score,
    ]])

    features_scaled = scaler.transform(features)
    score = float(model.predict(features_scaled)[0])
    score = max(0, min(100, round(score, 2)))

    # Determine placement likelihood
    if score >= 80:
        verdict = "Excellent"
        message = "You are highly placement-ready! Top companies are within your reach."
    elif score >= 65:
        verdict = "Good"
        message = "You have a solid profile. Focus on your weak areas to break into top-tier companies."
    elif score >= 50:
        verdict = "Moderate"
        message = "You have a decent foundation. Strengthen your DSA, projects, and open-source contributions."
    else:
        verdict = "Needs Improvement"
        message = "Focus on building core skills. Start with DSA, then work on projects and internships."

    # Feature-level breakdown
    feature_names = [
        "Academic Score", "DSA Skill", "Project Quality",
        "Experience", "Open Source", "Soft Skills", "Tech Stack"
    ]
    feature_values = [
        req.academic_score, req.dsa_skill, req.project_quality,
        req.experience_score, req.opensource_value, req.soft_skills,
        req.tech_stack_score
    ]
    max_values = [10, 10, 10, 10, 10, 10, 10]

    breakdown = []
    for name, val, mx in zip(feature_names, feature_values, max_values):
        pct = round((val / mx) * 100) if mx > 0 else 0
        breakdown.append({"name": name, "value": val, "max": mx, "percentage": pct})

    return {
        "readiness_score": score,
        "verdict": verdict,
        "message": message,
        "breakdown": breakdown,
    }


@app.post("/extract-profile")
async def extract_profile(req: ExtractRequest):
    """Use Gemini LLM to extract structured profile from free-form text."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    prompt = f"""You are a placement profile extraction assistant. 
Extract the following fields from the student's description. 
Return ONLY a valid JSON object with these exact keys:

{{
  "academic_score": <CGPA as float 0-10>,
  "dsa_skill": <DSA proficiency 1-10 integer>,
  "project_quality": <project quality 1-10 integer>,
  "experience_score": <internship/work experience 0-10 integer>,
  "opensource_value": <open source contributions, use 10 if they contribute, 1 if not>,
  "soft_skills": <communication/soft skills 1-10 integer>,
  "tech_stack_score": <tech stack breadth 1-10 integer>
}}

Rules:
- If CGPA is given on a 4.0 scale, convert to 10.0 scale
- If a field is not mentioned, infer a reasonable default (5 for most, 1 for opensource)
- tech_stack_score: count of distinct technologies mentioned, capped at 10
- dsa_skill: infer from competitive programming mentions, LeetCode, etc.
- Return ONLY the JSON, no markdown formatting, no explanation

Student description:
{req.text}"""

    try:
        llm = genai.GenerativeModel("gemini-2.0-flash")
        response = llm.generate_content(prompt)
        raw = response.text.strip()

        # Clean potential markdown wrapping
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

        profile = json.loads(raw)
        return {"profile": profile, "raw_extraction": raw}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=422, detail=f"LLM returned invalid JSON: {raw[:200]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


CHAT_SYSTEM_PROMPT = """You are PlaceMentor, a friendly and professional placement readiness mentor for engineering students.

Your job is to have a natural conversation to collect the student's profile information. You need to gather:
1. CGPA / Academic Score (0-10)
2. DSA Skill Level (how comfortable with data structures & algorithms, 1-10)
3. Project Quality (number and quality of projects, 1-10)
4. Experience (internships, work experience, 0-10)
5. Open Source Contributions (yes/no, what they did)
6. Soft Skills / Communication (1-10)
7. Tech Stack (what technologies they know)

Guidelines:
- Be conversational and encouraging, not interrogative
- Ask 1-2 questions at a time, not all at once
- When you feel you have enough information to extract all 7 fields, respond with EXACTLY this format at the end of your message:
  [PROFILE_COMPLETE]
  {"academic_score": X, "dsa_skill": X, "project_quality": X, "experience_score": X, "opensource_value": X, "soft_skills": X, "tech_stack_score": X}
  [/PROFILE_COMPLETE]
- The values inside the tags must be valid JSON
- opensource_value should be 10 if they contribute actively, 1 if they don't
- tech_stack_score should be based on how many distinct technologies they know (1-10)
- Until you have enough info, just continue the conversation naturally
- Start by greeting and asking about their academic background"""


@app.post("/chat")
async def chat(req: ChatMessage):
    """Guided conversational profiling with Gemini."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        # Fallback without API key - return a guided message
        return {
            "reply": "I'd love to help assess your placement readiness! However, the AI chat requires a Google API key to be configured. Please use the manual form instead, or set your GOOGLE_API_KEY in the .env file.",
            "profile_complete": False,
            "profile": None,
        }

    try:
        llm = genai.GenerativeModel("gemini-2.0-flash")

        # Build conversation history
        messages = [{"role": "user", "parts": [CHAT_SYSTEM_PROMPT + "\n\nStart the conversation now."]}]

        # Add a model greeting as the first response
        if not req.history:
            messages.append({
                "role": "model",
                "parts": ["Hey there! I'm PlaceMentor, your placement readiness guide. I'm here to help you understand how prepared you are for campus placements.\n\nLet's start with the basics - what's your current CGPA, and what branch/year are you in?"]
            })

        # Add conversation history
        for msg in req.history:
            role = "user" if msg.get("role") == "user" else "model"
            messages.append({"role": role, "parts": [msg["content"]]})

        # Add current message
        messages.append({"role": "user", "parts": [req.message]})

        chat_session = llm.start_chat(history=messages[:-1])
        response = chat_session.send_message(req.message)
        reply = response.text

        # Check if profile is complete
        profile = None
        profile_complete = False
        if "[PROFILE_COMPLETE]" in reply and "[/PROFILE_COMPLETE]" in reply:
            profile_complete = True
            try:
                json_str = reply.split("[PROFILE_COMPLETE]")[1].split("[/PROFILE_COMPLETE]")[0].strip()
                profile = json.loads(json_str)
            except (json.JSONDecodeError, IndexError):
                profile_complete = False

            # Clean the reply to remove the tags for display
            clean_reply = reply.split("[PROFILE_COMPLETE]")[0].strip()
            if not clean_reply:
                clean_reply = "Great, I have all the information I need! Let me calculate your placement readiness score."
            reply = clean_reply

        return {
            "reply": reply,
            "profile_complete": profile_complete,
            "profile": profile,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Parse uploaded resume (PDF/DOCX) and extract profile via LLM."""
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_google_api_key_here":
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY not configured")

    filename = file.filename.lower()
    content = await file.read()

    # Extract text based on file type
    text = ""
    if filename.endswith(".pdf"):
        from pypdf import PdfReader
        import io
        reader = PdfReader(io.BytesIO(content))
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    elif filename.endswith(".docx"):
        from docx import Document
        import io
        doc = Document(io.BytesIO(content))
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the file")

    # Use LLM to extract profile
    prompt = f"""You are an expert resume analyzer for engineering placement assessment.
Analyze this resume and extract the following fields.
Return ONLY a valid JSON object:

{{
  "academic_score": <CGPA as float 0-10, convert if on different scale>,
  "dsa_skill": <DSA proficiency 1-10 based on competitive programming, LeetCode, etc.>,
  "project_quality": <project quality 1-10 based on complexity and count>,
  "experience_score": <internship/work experience 0-10>,
  "opensource_value": <10 if open source contributions mentioned, 1 if not>,
  "soft_skills": <communication/leadership skills 1-10>,
  "tech_stack_score": <number of distinct technologies, capped at 10>,
  "name": "<student name>",
  "branch": "<engineering branch>",
  "tech_stack": "<comma-separated list of technologies>",
  "projects_summary": "<brief list of projects>",
  "experience_summary": "<brief internship/work summary>"
}}

Return ONLY the JSON, no markdown, no explanation.

Resume text:
{text[:3000]}"""

    try:
        llm = genai.GenerativeModel("gemini-2.0-flash")
        response = llm.generate_content(prompt)
        raw = response.text.strip()

        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith("json"):
            raw = raw[4:].strip()

        profile = json.loads(raw)
        return {"profile": profile, "resume_text_preview": text[:500]}
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail=f"LLM returned invalid JSON: {raw[:200]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/match-experiences")
async def match_experiences(req: ExtractRequest):
    """Find top matching interview experiences using cosine similarity."""
    count = experience_collection.count()
    if count == 0:
        return {"matches": [], "message": "No interview experiences ingested yet. Run ingest_experiences.py first."}

    try:
        results = experience_collection.query(
            query_texts=[req.text],
            n_results=min(5, count),
            include=["documents", "metadatas", "distances"],
        )

        matches = []
        if results["documents"] and results["documents"][0]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                similarity = max(0, round((1 - dist) * 100, 1))
                matches.append({
                    "content": doc,
                    "metadata": meta,
                    "similarity_pct": similarity,
                })

        return {"matches": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ── Run ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
