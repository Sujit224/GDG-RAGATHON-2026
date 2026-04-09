from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from rag_engine import RAGEngine

app = FastAPI(title="Lucknow Foodie Guide API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Starting server... initialising RAG Engine...")
rag = RAGEngine()
print("RAG Engine initialised successfully.")

class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] = []

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        result = rag.process_chat(req.message, req.history)
        return {
            "reply": result["reply"],
            "restaurants": [r.__dict__ for r in result["restaurants"]],
            "sources": [r.id for r in result["restaurants"]]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/restaurants")
async def get_restaurants(
    diet: Optional[str] = None,
    budget_max: Optional[int] = None,
    vibe: Optional[str] = None,
    area: Optional[str] = None,
    dish: Optional[str] = None,
    delivery: Optional[bool] = None,
    sort_by: str = "rating"
):
    # Map 'All' from frontend to None
    if diet == "All": diet = None
    if area == "All Areas": area = None

    if diet == "Both": diet = "veg" # In db.search, "Both" is not a standard query value but 'veg' or 'non-veg'. Wait, 'Both' diet means the restaurant serves Both. Let db.search handle it as is by not passing it if 'All'. The UI might send 'Both' to mean it serves both veg and non-veg.
    
    results = rag.db.search(
        diet=diet,
        budget_max=budget_max,
        vibe=vibe,
        area=area,
        dish=dish,
        delivery=delivery,
        sort_by=sort_by,
        top_n=50
    )
    return [r.__dict__ for r in results]

@app.get("/api/restaurant/{id}")
async def get_restaurant(id: str):
    r = rag.db.get_by_id(id)
    if r:
        return r.__dict__
    raise HTTPException(status_code=404, detail="Restaurant not found")

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "restaurants_loaded": len(rag.db.restaurants),
        "chroma_ready": True
    }
