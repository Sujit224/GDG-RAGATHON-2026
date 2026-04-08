import json
import os
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

def initialize_vector_db():
    # Load the 50+ restaurant dataset
    json_path = os.path.join("..", "dataset", "lucknow_eats.json")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    documents = []
    for item in data:
        # HUMANIZED LOGIC: We combine fields into a 'story' for better semantic matching
        content = (f"{item['name']} is located in {item['location']}. "
                   f"It has a {item['vibe']} vibe and is famous for {item['signature_dish']}. "
                   f"The budget is {item['budget']} with an average price of ₹{item['avg_price']}.")
        
        # Metadata is CRITICAL for Member 1's filtering logic
        doc = Document(
            page_content=content,
            metadata={
                "name": item['name'],
                "budget": item['budget'],
                "avg_price": item['avg_price'],
                "lat": item['lat'],
                "lon": item['lon'],
                "vibe": item['vibe']
            }
        )
        documents.append(doc)
    
    # Initialize Google Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    # Create and persist the database
    vector_db = Chroma.from_documents(
        documents=documents, 
        embedding=embeddings, 
        persist_directory="./food_db"
    )
    print("✅ Vector Database Initialized with 50+ Lucknow Spots!")
    return vector_db

if __name__ == "__main__":
    initialize_vector_db()