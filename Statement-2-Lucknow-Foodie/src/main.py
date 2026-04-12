import os
import json
import pickle
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(title="Gourmet Guide — Lucknow Foodie RAG API", version="2.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RestaurantVectorStore:
    def __init__(self, db_dir: str):
        faiss_path = os.path.join(db_dir, 'restaurants.faiss')
        meta_path  = os.path.join(db_dir, 'restaurants_meta.pkl')
        
        print(f"[RAG] Loading FAISS vector store from: {db_dir}")
        self.index = faiss.read_index(faiss_path)
        
        with open(meta_path, 'rb') as f:
            self.data = pickle.load(f)
        
        print(f"[RAG] {len(self.data)} restaurant vectors loaded.")
        print("[RAG] Initializing SentenceTransformer embedding model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        print("[RAG] Vector store ready ✅")

    def search(self, query: str, k: int = 5) -> list:
        query_embedding = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                doc = dict(self.data[idx])
                doc['_similarity_score'] = float(1 / (1 + dist))
                results.append(doc)
        
        results.sort(key=lambda x: x['_similarity_score'], reverse=True)
        return results



BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'vector_db')

vector_store: Optional[RestaurantVectorStore] = None
try:
    vector_store = RestaurantVectorStore(DB_PATH)
except Exception as e:
    print(f"[RAG] ⚠️  Could not load vector store: {e}")
    print("[RAG] Please run `python3 src/ingest.py` first.")


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
llm = None



if GEMINI_API_KEY:
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GEMINI_API_KEY,
            temperature=0.75,
            max_retries=0,
        )
        print("[LLM] Google Gemini initialized ✅")
    except Exception as e:
        print(f"[LLM] ⚠️  Gemini init error: {e}")
else:
     print("[LLM] ⚠️  GEMINI_API_KEY not set. Running in retrieval-only mode.")



RAG_PROMPT = PromptTemplate(
    input_variables=["context", "query"],
    template="""You are **"Gourmet Guide"** — Lucknow's most sophisticated AI culinary concierge, designed exclusively for IIIT Lucknow students.

You have access to a curated database of the finest restaurants in Lucknow, built using Retrieval-Augmented Generation (RAG) technology with FAISS vector search and Google Gemini.

--- RETRIEVED RESTAURANT CONTEXT (from your vector knowledge base) ---
{context}
--- END CONTEXT ---

Student Query: {query}

INSTRUCTIONS:
1. **Greet warmly** with a one-liner that matches the query's vibe (e.g., budget→thrifty, date→romantic, party→fun).
2. **Recommend 2-3 top matches** from the retrieved context ONLY. Do not hallucinate restaurants outside this list.
3. **Bold every Restaurant Name** and *italicize every dish name*.
4. Use a `> blockquote` to describe the **Vibe** of each recommendation.
5. Mention the **Budget** symbol (₹/₹₹/₹₹₹) and **rating** for clarity.
6. If relevant, add a practical **Pro Tip** for IIIT Lucknow students (e.g., best time to visit, how to get there from campus).
7. End with an inviting call-to-action to ask more.
8. Keep the tone elegant, concise, and conversational. Max 200 words.
9. Format: Use markdown for **bold**, *italic*, > blockquote, and bullet lists.
"""
)


class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict]
    retrieved_count: int


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    if not req.query or len(req.query.strip()) < 2:
        raise HTTPException(status_code=400, detail="Query must be at least 2 characters.")
    
    query = req.query.strip()
    print(f"\n[QUERY] '{query}'")


    if not vector_store:
        raise HTTPException(
            status_code=503,
            detail="Vector store not initialized. Run `python3 src/ingest.py` first."
        )
    
    top_k = vector_store.search(query, k=4)
    print(f"[RETRIEVE] Found {len(top_k)} results.")
    
    
    clean_sources = []
    for r in top_k:
        src = {k: v for k, v in r.items() if not k.startswith('_')}
        clean_sources.append(src)

   
    context_blocks = []
    for i, r in enumerate(top_k, 1):
        cuisine = ', '.join(r['cuisine']) if isinstance(r['cuisine'], list) else r.get('cuisine', '')
        vibe    = ', '.join(r['vibe'])    if isinstance(r['vibe'], list)    else r.get('vibe', '')
        dishes  = ', '.join(r['signature_dishes']) if isinstance(r['signature_dishes'], list) else r.get('signature_dishes', '')
        
        block = (
            f"[{i}] **{r['name']}** | Location: {r.get('location','N/A')} | "
            f"Budget: {r.get('budget','?')} | Rating: {r.get('rating','?')}★\n"
            f"   Cuisine: {cuisine}\n"
            f"   Vibe: {vibe}\n"
            f"   Signature Dishes: {dishes}\n"
            f"   About: {r.get('description','')}"
        )
        context_blocks.append(block)
    
    context_str = "\n\n".join(context_blocks)

  
    answer_text = ""
    
    # if llm:
    #     try:
    #         prompt_val = RAG_PROMPT.format(context=context_str, query=query)
    #         response   = llm.invoke(prompt_val)
    #         answer_text = response.content
    #     except Exception as e:
    #         print(f"[LLM ERROR] {e}")
    #         answer_text = _build_fallback_response(top_k, query)
    if llm:
        try:
            import asyncio
            from concurrent.futures import TimeoutError
            prompt_val = RAG_PROMPT.format(context=context_str, query=query)
            response   = await asyncio.wait_for(
                asyncio.get_event_loop().run_in_executor(
                    None, lambda: llm.invoke(prompt_val)
                ),
                timeout=8.0   # give up after 8 seconds max
            )
            answer_text = response.content
        except Exception as e:
            print(f"[LLM ERROR - falling back] {type(e).__name__}")
            answer_text = _build_fallback_response(top_k, query)

    else:
        answer_text = _build_fallback_response(top_k, query)

    return ChatResponse(
        answer=answer_text,
        sources=clean_sources,
        retrieved_count=len(top_k)
    )


def _build_fallback_response(restaurants: list, query: str) -> str:
    lines = [f"Here are my top picks for: *\"{query}\"*\n"]
    for r in restaurants[:3]:
        dishes = ', '.join(r['signature_dishes']) if isinstance(r['signature_dishes'], list) else r.get('signature_dishes', '')
        vibe   = ', '.join(r['vibe'])             if isinstance(r['vibe'], list)             else r.get('vibe', '')
        lines.append(
            f"**{r['name']}** ({r.get('budget','₹')} | ⭐ {r.get('rating','')})\n"
            f"> 📍 {r.get('location','')} — *Vibe: {vibe}*\n"
            f"Signature: *{dishes}*\n"
        )
    lines.append("\n*(Set your `GEMINI_API_KEY` in `.env` for AI-powered recommendations!)*")
    return "\n".join(lines)



@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "vector_store": "loaded" if vector_store else "not_loaded",
        "llm": "gemini" if llm else "fallback_mode",
        "restaurants": len(vector_store.data) if vector_store else 0
    }



STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


