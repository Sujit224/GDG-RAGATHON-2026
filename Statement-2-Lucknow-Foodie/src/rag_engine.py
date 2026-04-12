import warnings
warnings.filterwarnings("ignore")
import os 
from langchain_community.document_loaders import CSVLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def initialize_rag():
    
    data_path = "data/restaurants.csv"
    
    if not os.path.exists(data_path):
        print(f"[!] Error: {data_path} not found. Please create the CSV first.")
        return None

    print("--- Initializing Lucknow Foodie Search Engine ---")
    
    
    loader = CSVLoader(file_path=data_path)
    documents = loader.load()
    
    
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    
    vector_db = Chroma.from_documents(
        documents, 
        embeddings, 
        persist_directory="./vectorstore"
    )
    print("--- System Ready! ---")
    return vector_db

def chat():
    db = initialize_rag()
    if not db:
        return

    print("\nWelcome to the Lucknow Foodie Bot! Type 'exit' to quit.")
    
    while True:
        user_query = input("\nYou: ")
        
        if user_query.lower() in ['exit', 'quit', 'bye']:
            print("Happy eating! Goodbye.")
            break
            
        
        results = db.similarity_search(user_query, k=2)
        
        if results:
            print("\nAI Recommendation:")
            for i, res in enumerate(results):
                print(f"Suggestion {i+1}:")
                print(res.page_content)
                print("-" * 20)
        else:
            print("Sorry, I couldn't find any restaurants matching that description.")

if __name__ == "__main__":
    chat()