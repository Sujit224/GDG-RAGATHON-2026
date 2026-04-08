import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Import the updated function from your loader
from loader import load_and_split_documents

# Setup Environment
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, "..", ".env"))

def create_vector_db(docs_dir):
    # 1. Use the loader to get the chunks
    chunks = load_and_split_documents(docs_dir)
    
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY not found! Check your .env file.")
        
    # 2. Create Embeddings
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        task_type="retrieval_document"
    )
    
    print("--- Creating Embeddings (This may take a moment) ---")
    persist_dir = os.path.join(current_dir, "..", "chroma_db")
    
    # 3. Store in Chroma
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir
    )
    
    print(f"Success! Multi-document Vector database created at: {persist_dir}")
    return vector_db

if __name__ == "__main__":
    # Point to the docs folder instead of a single file
    docs_folder = os.path.join(current_dir, "..", "docs")
    
    # Auto-create the folder if it doesn't exist
    os.makedirs(docs_folder, exist_ok=True)
    
    print("Ensure you have placed 'TITAN SECURE.pdf' (and any others) inside the 'docs' folder.")
    create_vector_db(docs_folder)