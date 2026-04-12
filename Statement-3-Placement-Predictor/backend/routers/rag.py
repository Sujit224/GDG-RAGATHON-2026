from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from services.rag_service import retrieve_experiences

router = APIRouter()

class RAGRequest(BaseModel):
    tech_stack: List[str]
    top_k: int = 3

@router.post("/rag")
async def rag_retrieve(req: RAGRequest):
    experiences = retrieve_experiences(req.tech_stack, req.top_k)
    return {"experiences": experiences}
