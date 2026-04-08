from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict
from services.llm_service import chat_with_student, extract_profile

router = APIRouter()

class ChatRequest(BaseModel):
    messages: list[dict]   # [{role: "user"/"assistant", content: "..."}]

class ChatResponse(BaseModel):
    reply: str
    profile_complete: bool
    profile: Optional[Dict] = None

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    reply = chat_with_student(req.messages)
    is_complete = "PROFILE_COMPLETE" in reply
    profile = None
    if is_complete:
        reply = reply.replace("PROFILE_COMPLETE", "").strip()
        profile = extract_profile(req.messages + [{"role": "assistant", "content": reply}])
    return ChatResponse(reply=reply, profile_complete=is_complete, profile=profile)
