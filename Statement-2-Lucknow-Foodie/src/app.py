"""
FastAPI Backend for Lucknow Foodie Guide
==========================================
Serves the chat API and static frontend.

Usage:
    cd Statement-2-Lucknow-Foodie
    uvicorn src.app:app --reload --port 8000
"""

import os
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag import FoodieRAG
from src.ingest import ingest, EMBEDDINGS_PATH

# ---------------------------------------------------------------------------
# Lifespan — run ingestion on startup if DB doesn't exist
# ---------------------------------------------------------------------------
rag_engine: FoodieRAG | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    On startup:
    1. Check if ChromaDB collection exists → if not, run ingestion
    2. Initialise the RAG engine
    """
    global rag_engine

    # Check if embeddings are populated
    if not os.path.exists(EMBEDDINGS_PATH):
        print("🔄 First run detected — running ingestion pipeline...")
        ingest()
        print("✅ Ingestion complete!")
    else:
        print("✅ Embeddings found.")

    # Initialise RAG engine
    print("🚀 Initialising Foodie RAG engine...")
    rag_engine = FoodieRAG()
    print("✅ Lucknow Foodie Guide is ready!")

    yield  # ← app runs here

    print("👋 Shutting down Lucknow Foodie Guide.")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Lucknow Foodie Guide 🍽️",
    description="A RAG-powered restaurant recommendation chatbot for IIIT Lucknow students",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend on any origin during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (frontend)
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str
    restaurants_found: int


class RestaurantSummary(BaseModel):
    name: str
    area: str
    cuisine: str
    price_range: str
    veg_nonveg: str
    rating: float
    distance_from_iiit_km: float


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the main chat UI."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse(
        {"message": "Lucknow Foodie Guide API 🍽️ — Frontend not found. Use /docs for API."},
        status_code=200,
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint.
    Accepts a user message, runs hybrid RAG search,
    and returns an LLM-generated response.
    """
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialised yet.")

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    # Run RAG pipeline
    reply = rag_engine.query(request.message)
    matches = rag_engine.search(request.message)

    return ChatResponse(
        reply=reply,
        restaurants_found=len(matches),
    )


@app.post("/reset")
async def reset_chat():
    """Clear conversation history for a fresh start."""
    if rag_engine:
        rag_engine.reset_history()
    return {"message": "Conversation history cleared! 🔄"}


@app.get("/restaurants", response_model=list[RestaurantSummary])
async def list_restaurants():
    """Return all restaurants in the database (for browsing)."""
    if not rag_engine:
        raise HTTPException(status_code=503, detail="RAG engine not initialised yet.")

    all_restaurants = rag_engine.get_all_restaurants()
    return [
        RestaurantSummary(
            name=r.get("name", "Unknown"),
            area=r.get("area", "N/A"),
            cuisine=r.get("cuisine", "N/A"),
            price_range=r.get("price_range", "N/A"),
            veg_nonveg=r.get("veg_nonveg", "N/A"),
            rating=r.get("rating", 0.0),
            distance_from_iiit_km=r.get("distance_from_iiit_km", 0.0),
        )
        for r in all_restaurants
    ]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "engine_ready": rag_engine is not None,
        "service": "Lucknow Foodie Guide 🍽️",
    }


# ---------------------------------------------------------------------------
# Run directly with: python src/app.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
