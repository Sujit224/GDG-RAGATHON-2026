import fitz
import chromadb
import re
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pdf_path = os.path.join(BASE_DIR, "data", "INTERVIEW EXPERIENCES.pdf")
db_path = os.path.join(BASE_DIR, "chroma_db")
collection_name = "interview_experiences"

client = chromadb.PersistentClient(path=db_path)

def parse_experiences():
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text() + "\n"

    # Specific parsing to split into individual experiences:
    # They start with e.g. "1. Google Software Engineer Interview Experience"
    pattern = r"\n(\d+\.\s+.*?Interview Experience)\n"
    parts = re.split(pattern, "\n" + full_text)
    
    experiences = []
    for i in range(1, len(parts), 2):
        title = parts[i].strip()
        body = parts[i+1].strip()
        experiences.append({
            "title": title,
            "text": title + "\n" + body
        })
    
    print(f"Extracted {len(experiences)} experiences from PDF.")
    return experiences

def index_experiences():
    try:
        collection = client.get_collection(name=collection_name)
        print("Collection already exists, skipping indexing.")
        return
    except:
        collection = client.create_collection(name=collection_name)

    experiences = parse_experiences()
    
    documents = [exp["text"] for exp in experiences]
    metadatas = [{"title": exp["title"]} for exp in experiences]
    ids = [f"exp_{i}" for i in range(len(experiences))]
    
    print("Adding documents to ChromaDB...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Indexing complete.")

def get_top_experiences(profile_query, top_k=3):
    collection = client.get_collection(name=collection_name)
    results = collection.query(
        query_texts=[profile_query],
        n_results=top_k
    )
    
    recommendations = []
    if results['documents'] and len(results['documents']) > 0:
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            recommendations.append({
                "title": meta["title"],
                "content": doc
            })
    return recommendations

if __name__ == "__main__":
    index_experiences()
