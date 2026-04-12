import os
import json
from dotenv import load_dotenv
load_dotenv()
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document

DB_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "../../dataset/restaurants.json")

def load_dataset():
    with open(DATASET_PATH, "r") as f:
        return json.load(f)

def get_vectorstore():
    # Attempt to load Google API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Warning: GEMINI_API_KEY not found in environment.")

    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    if os.path.exists(DB_DIR) and len(os.listdir(DB_DIR)) > 0:
        return Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        
    print("Initializing Chroma DB with dataset...")
    data = load_dataset()
    docs = []
    for r in data:
        content = (
            f"Name: {r['name']}\n"
            f"Location: {r['location']}\n"
            f"Vibe: {r['vibe']}\n"
            f"Budget: {r['budget']}\n"
            f"Dietary: {r['dietary']}\n"
            f"Signature Dishes: {', '.join(r['signature_dishes'])}\n"
            f"Reviews: {r['reviews']}\n"
            f"Hours: {r['hours']}"
        )
        metadata = {"name": r["name"], "location": r["location"], "vibe": r["vibe"]}
        docs.append(Document(page_content=content, metadata=metadata))
        
    vectorstore = Chroma.from_documents(docs, embeddings, persist_directory=DB_DIR)
    return vectorstore

def query_restaurants(query: str, k: int = 5):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search(query, k=k)
    return results

if __name__ == "__main__":
    v = get_vectorstore()
    print("Vectorstore initialized.")
