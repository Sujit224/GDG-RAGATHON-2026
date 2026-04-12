from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import uvicorn

try:
    from .models import StudentProfile, AnalysisResult, ExperienceMatch
    from .profiler import ChatProfiler
    from .regression_engine import predict_score
    from .rag_engine import rag_engine
    from .resume_parser import parse_resume
except (ImportError, ValueError):
    from models import StudentProfile, AnalysisResult, ExperienceMatch
    from profiler import ChatProfiler
    from regression_engine import predict_score
    from rag_engine import rag_engine
    from resume_parser import parse_resume

app = FastAPI(title="PlacementIQ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sessions (Simple in-memory store for demo)
sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.session_id not in sessions:
        sessions[req.session_id] = ChatProfiler()
        # If the user sent a message, we might want to skip the greeting 
        # but let's just initialize and then process the message.
        # Actually, let's return the greeting first if the message is 'INIT'
        if req.message == "INIT":
            greeting = sessions[req.session_id].get_greeting()
            return {"reply": greeting, "complete": False}
    
    profiler = sessions[req.session_id]
    reply = profiler.chat_sync(req.message)
    return {"reply": reply, "complete": profiler.is_complete()}

@app.get("/analyze/{session_id}")
async def analyze(session_id: str):
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    profiler = sessions[session_id]
    profile = profiler.extract_profile()
    
    score = predict_score(profile)
    matches = rag_engine.get_top_matches(profile)
    
    return AnalysisResult(
        profile=profile,
        readiness_score=score,
        top_experiences=matches
    )

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    contents = await file.read()
    profile = parse_resume(contents, file.filename)
    
    if not profile.is_complete():
        raise HTTPException(status_code=400, detail="Failed to extract profile from resume.")
    
    score = predict_score(profile)
    matches = rag_engine.get_top_matches(profile)
    
    return AnalysisResult(
        profile=profile,
        readiness_score=score,
        top_experiences=matches
    )

# Static files
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

if not os.path.exists(FRONTEND_DIR):
    os.makedirs(FRONTEND_DIR)

@app.get("/")
async def read_index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
