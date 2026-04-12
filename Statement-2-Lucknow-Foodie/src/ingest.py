import os
import json
import pickle
from sentence_transformers import SentenceTransformer
import faiss

def run_ingestion():
    dataset_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset', 'restaurants.json')
    vector_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'vector_db')
    
    # Ensure vector_db output dir exists
    os.makedirs(vector_db_path, exist_ok=True)
    
    print(f"Loading dataset from: {dataset_path}")
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Loaded {len(data)} restaurants. Building contextual documents...")
    
    documents = []
    for r in data:
        # Create rich text string for vectorization
        text = (f"Name: {r['name']}. Location: {r['location']}. "
                f"Cuisine: {', '.join(r['cuisine'])}. Budget: {r['budget']}. "
                f"Vibe: {', '.join(r['vibe'])}. Signature Dishes: {', '.join(r['signature_dishes'])}. "
                f"Description: {r['description']}")
        documents.append(text)
        
    print("Downloading/Loading Sentence Transformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Computing embeddings for all restaurants...")
    embeddings = model.encode(documents).astype('float32')
    
    print("Initializing FAISS Index...")
    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    
    # Save the index and metadata
    faiss_file = os.path.join(vector_db_path, "restaurants.faiss")
    meta_file  = os.path.join(vector_db_path, "restaurants_meta.pkl")
    
    print(f"Saving FAISS index to {faiss_file}...")
    faiss.write_index(index, faiss_file)
    
    print(f"Saving Metadata to {meta_file}...")
    with open(meta_file, 'wb') as f:
        pickle.dump(data, f)
        
    print("✅ Ingestion complete! The API server can now load instantaneously.")

if __name__ == "__main__":
    run_ingestion()
