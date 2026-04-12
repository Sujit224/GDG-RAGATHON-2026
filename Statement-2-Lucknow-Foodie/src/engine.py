import os
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# 1. SETUP: Load keys and define paths
load_dotenv() 
current_dir = os.path.dirname(os.path.abspath(__file__))
dataset_path = os.path.join(current_dir, "..", "dataset", "lucknow_eateries.csv")
persist_directory = os.path.join(current_dir, "food_index_db") # This fixes the NameError

# 2. INGESTION: Load your CSV
if not os.path.exists(dataset_path):
    print(f"❌ File not found at: {dataset_path}")
else:
    # Ensure 'name' matches your CSV column header exactly
    loader = CSVLoader(file_path=dataset_path, source_column="name") 
    docs = loader.load()

    if docs:
        print(f"📦 Successfully loaded {len(docs)} eateries.")

        # 3. VECTOR DB: This is the 'Brain' of your RAG
        print("🧠 Creating vector embeddings... please wait.")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vector_db = Chroma(
            embedding_function=embeddings,
            persist_directory=persist_directory,
            collection_name="lucknow_foodie"
        )
        
        print(f"✅ Success! Your database is saved at: {persist_directory}")
    else:
        print("⚠️ The CSV is empty. Add some restaurants to your dataset folder!")