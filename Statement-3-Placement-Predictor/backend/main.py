from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, predict, rag
from services.ml_service import train_and_save_model
from services.rag_service import build_faiss_index
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PlaceIQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    train_and_save_model()   # trains regression model on CSV data
    build_faiss_index()      # builds FAISS index from PDF

app.include_router(chat.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(rag.router, prefix="/api")
