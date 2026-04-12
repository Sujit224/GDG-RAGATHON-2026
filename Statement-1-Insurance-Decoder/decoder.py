
# import os
# os.environ["ANONYMIZED_TELEMETRY"] = "False"  
# os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
# import argparse
# import glob
# import re
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_core.documents import Document
# from sentence_transformers import SentenceTransformer
# import chromadb


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")
# DATA_DIR = os.path.join(BASE_DIR, "docs")
# COLLECTION_NAME = "fine_print"

# def get_chroma_collection():
#     client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
#     collection = client.get_or_create_collection(name=COLLECTION_NAME)
#     return collection

# def ingest_documents():
#     print("Ingesting documents...")
#     files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
#     docs = []
    
#     for file_path in files:
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
            
#         doc_name = os.path.basename(file_path)
        
        
#         sections = re.split(r"(Section \d+:.*?)\n", content)
        
#         current_section_name = "General"
        
       
        
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=500,
#             chunk_overlap=50
#         )
        
#         chunks = text_splitter.split_text(content)
        
#         for chunk in chunks:
           
#             section_match = re.search(r"(Section \d+:[^\n]+)", chunk)
#             clause_match = re.search(r"(Clause \d+\.\d+:[^\n]+)", chunk)
            
#             meta_section = section_match.group(1) if section_match else "Unknown Section"
#             meta_clause = clause_match.group(1) if clause_match else "Unknown Clause"
            
            
            
#             docs.append({
#                 "text": chunk,
#                 "metadata": {
#                     "source": doc_name,
#                     "section": meta_section,
#                     "clause": meta_clause
#                 }
#             })
            
    
#     print(f"Loading embedding model... Processing {len(docs)} chunks.")
#     embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
#     collection = get_chroma_collection()
    
#     documents = [d["text"] for d in docs]
#     metadatas = [d["metadata"] for d in docs]
#     ids = [f"id_{i}" for i in range(len(docs))]
    
#     embeddings = embedder.encode(documents).tolist()
    
#     collection.add(
#         ids=ids,
#         embeddings=embeddings,
#         metadatas=metadatas,
#         documents=documents
#     )
    
#     print("Ingestion complete.")

# def query_system(user_query, document_filter=None, topic_filter=None):
#     print("Loading query subsystem...")
#     embedder = SentenceTransformer('all-MiniLM-L6-v2')
#     collection = get_chroma_collection()
    
#     query_embedding = embedder.encode([user_query]).tolist()
    
#     where_clause = {}
#     if document_filter:
#         where_clause["source"] = {"$eq": document_filter}
    
    
#     results = collection.query(
#         query_embeddings=query_embedding,
#         n_results=3,
#         where=where_clause if where_clause else None
#     )
    
#     if not results["documents"] or not results["documents"][0]:
#         print("No relevant clauses found.")
#         return
        
#     retrieved_texts = results["documents"][0]
#     retrieved_metadatas = results["metadatas"][0]
    
    
#     if topic_filter:
#         filtered_texts = []
#         filtered_metas = []
#         for text, meta in zip(retrieved_texts, retrieved_metadatas):
#             if topic_filter.lower() in text.lower() or topic_filter.lower() in meta["section"].lower() or topic_filter.lower() in meta["clause"].lower():
#                 filtered_texts.append(text)
#                 filtered_metas.append(meta)
#         retrieved_texts = filtered_texts
#         retrieved_metadatas = filtered_metas

#     if not retrieved_texts:
#         print("No clauses match your specific topic filter.")
#         return

#     context = "\n".join(retrieved_texts)
    
#     from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
#     print("Loading LLM for ELI5 simplification (this might take a moment without GPU)...")
#     tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
#     model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    
    
#     prompt = f"Simplify the following legal text for a 5 year old. Context: {context} Question: {user_query}. Answer simply:"
    
#     inputs = tokenizer(prompt, return_tensors="pt")
#     outputs = model.generate(**inputs, max_new_tokens=150)
#     answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
#     print("\n" + "="*50)
#     print("🤖 FINE PRINT DECODER:")
#     print("="*50)
#     print(f"Question: {user_query}")
#     if document_filter: print(f"Applies to: {document_filter}")
#     print("\n📝 ELI5 Answer:")
#     print(answer)
#     print("\n⚖️  Source Attribution:")
#     for meta in retrieved_metadatas:
#         print(f"  - Document: {meta['source']}")
#         print(f"    {meta['section']}")
#         if meta['clause'] != "Unknown Clause":
#             print(f"    {meta['clause']}")
#     print("="*50)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Fine Print Decoder - RAG System")
#     parser.add_argument("action", choices=["ingest", "query"], help="Action to perform")
#     parser.add_argument("--query", type=str, help="Question to ask")
#     parser.add_argument("--filter-doc", type=str, help="Filter by document name (e.g. Titan_Secure_Health_Insurance_Policy.txt)")
#     parser.add_argument("--filter-topic", type=str, help="Smart filtering keyword (e.g. coverage, penalties, exclusions)")
    
#     args = parser.parse_args()
    
#     if args.action == "ingest":
#         ingest_documents()
#     elif args.action == "query":
#         if not args.query:
#             print("Please provide a --query!")
#         else:
#             query_system(args.query, args.filter_doc, args.filter_topic)


import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # Disable chromadb telemetry
os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
import argparse
import glob
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import chromadb

# ------ NEW IMPORTS FOR THE WEB UI ------
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Ensure paths are relative to the script itself, not where you call it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")
DATA_DIR = os.path.join(BASE_DIR, "docs")
COLLECTION_NAME = "fine_print"

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection

def ingest_documents():
    print("Ingesting documents...")
    files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    docs = []
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        doc_name = os.path.basename(file_path)
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        chunks = text_splitter.split_text(content)
        
        for chunk in chunks:
            # Extract section/clause if present in chunk
            section_match = re.search(r"(Section \d+:[^\n]+)", chunk)
            clause_match = re.search(r"(Clause \d+\.\d+:[^\n]+)", chunk)
            
            meta_section = section_match.group(1) if section_match else "Unknown Section"
            meta_clause = clause_match.group(1) if clause_match else "Unknown Clause"
            
            docs.append({
                "text": chunk,
                "metadata": {
                    "source": doc_name,
                    "section": meta_section,
                    "clause": meta_clause
                }
            })
            
    print(f"Loading embedding model... Processing {len(docs)} chunks.")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    collection = get_chroma_collection()
    
    documents = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]
    ids = [f"id_{i}" for i in range(len(docs))]
    
    embeddings = embedder.encode(documents).tolist()
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    print("Ingestion complete.")

def query_system(user_query, document_filter=None, topic_filter=None):
    print("Loading query subsystem...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    collection = get_chroma_collection()
    
    query_embedding = embedder.encode([user_query]).tolist()
    
    where_clause = {}
    if document_filter:
        where_clause["source"] = {"$eq": document_filter}
    
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        where=where_clause if where_clause else None
    )
    
    if not results["documents"] or not results["documents"][0]:
        return {"error": "No relevant clauses found."}
        
    retrieved_texts = results["documents"][0]
    retrieved_metadatas = results["metadatas"][0]
    
    if topic_filter:
        filtered_texts = []
        filtered_metas = []
        for text, meta in zip(retrieved_texts, retrieved_metadatas):
            if topic_filter.lower() in text.lower() or topic_filter.lower() in meta["section"].lower() or topic_filter.lower() in meta["clause"].lower():
                filtered_texts.append(text)
                filtered_metas.append(meta)
        retrieved_texts = filtered_texts
        retrieved_metadatas = filtered_metas

    if not retrieved_texts:
        return {"error": "No clauses match your specific topic filter."}

    context = "\n".join(retrieved_texts)
    
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("Loading LLM for ELI5 simplification (this might take a moment without GPU)...")
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    
    prompt = f"Simplify the following legal text for a 5 year old. Context: {context} Question: {user_query}. Answer simply:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # ------ CHANGED TO RETURN JSON INSTEAD OF PRINTING ------
    target_meta = retrieved_metadatas[0] if retrieved_metadatas else {}
    return {
        "eli5": answer,
        "original_text": retrieved_texts[0],  # Give the UI the top matched text
        "sources": {
            "section": target_meta.get("section", "Unknown Section"),
            "clause": target_meta.get("clause", "Unknown Clause"),
            "page": target_meta.get("source", "Unknown Document")
        }
    }


# ====================================================================
#  WEB SERVER (FASTAPI) LOGIC
# ====================================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/api/decode")
async def api_decode(request: QueryRequest):
    result = query_system(request.query)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

# Serve your UI code (index.html, styles.css, app.js) from the "static" folder
STATIC_DIR = os.path.join(BASE_DIR, "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine Print Decoder - RAG System")
    parser.add_argument("action", nargs="?", choices=["ingest", "query", "serve"], default="serve", help="Action to perform. Default is 'serve'")
    parser.add_argument("--query", type=str, help="Question to ask")
    
    args = parser.parse_args()
    
    if args.action == "ingest":
        ingest_documents()
    elif args.action == "query":
        if not args.query:
            print("Please provide a --query!")
        else:
            print(query_system(args.query))
    elif args.action == "serve":
        # Boots up the web UI using uvicorn
        import uvicorn
        print("🚀 Starting Web UI on http://localhost:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)

