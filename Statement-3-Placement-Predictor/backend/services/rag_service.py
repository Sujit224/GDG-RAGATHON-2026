from sentence_transformers import SentenceTransformer
import faiss, numpy as np, json, os
from services.pdf_parser import parse_interview_experiences

MODEL_NAME = "all-MiniLM-L6-v2"
INDEX_PATH = "models/faiss_index"
EXPERIENCES_PATH = "models/experiences.json"

embedder = SentenceTransformer(MODEL_NAME)
index = None
experiences = []

def build_faiss_index():
    global index, experiences
    
    if os.path.exists(f"{INDEX_PATH}/index.bin") and os.path.exists(EXPERIENCES_PATH):
        index = faiss.read_index(f"{INDEX_PATH}/index.bin")
        with open(EXPERIENCES_PATH, "r") as f:
            experiences = json.load(f)
        return
        
    experiences = parse_interview_experiences("data/interview_experiences.pdf")
    if not experiences:
        print("No experiences parsed.")
        return
        
    texts = [e["text"] for e in experiences]
    embeddings = embedder.encode(texts, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    os.makedirs(INDEX_PATH, exist_ok=True)
    faiss.write_index(index, f"{INDEX_PATH}/index.bin")
    with open(EXPERIENCES_PATH, "w") as f:
        json.dump(experiences, f)

def retrieve_experiences(tech_stack: list[str], top_k: int = 3) -> list[dict]:
    """
    Query vector DB with user's tech stack as the query string.
    Returns top_k most relevant interview experiences.
    """
    if index is None or not experiences:
        return []
        
    query = " ".join(tech_stack)
    if not query.strip():
        query = "software engineering"
        
    query_vec = embedder.encode([query], convert_to_numpy=True)
    D, I = index.search(query_vec, top_k)
    return [experiences[i] for i in I[0] if i < len(experiences)]
