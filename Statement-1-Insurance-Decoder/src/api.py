import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

import sys
sys.path.append(os.path.dirname(__file__))

# Imports for RAG backend processing
from rag_chain import get_rag_chain
from ingest import process_file_to_db

app = FastAPI(title="Insurance Decoder API")

# Update CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    status: str

@app.post("/api/chat", response_model=QueryResponse)
def chat_with_policy(request: QueryRequest):
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
         raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing or invalid.")
         
    try:
        rag_chain = get_rag_chain()
        result = rag_chain.invoke(request.query)
        return QueryResponse(response=result, status="success")
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Vector search database not found. Please upload a PDF first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(docs_dir, exist_ok=True)
    
    file_path = os.path.join(docs_dir, file.filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    try:
        # Trigger DB Ingestion natively
        process_file_to_db(file_path)
        return {"status": "success", "message": f"Successfully processed {file.filename}."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")

@app.get("/api/status")
def health_check():
    db_exists = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
    key_exists = bool(os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY") != "your_groq_api_key_here")
    return {
        "api": "healthy",
        "chroma_db_ready": db_exists,
        "groq_key_ready": key_exists
    }
