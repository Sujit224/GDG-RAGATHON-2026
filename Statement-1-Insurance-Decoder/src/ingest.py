import os
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load environment variables
load_dotenv()

# Define paths
FILE_DIR = os.path.dirname(__file__)
DB_DIR = os.path.join(FILE_DIR, "..", "chroma_db")

def parse_pdf_to_documents(pdf_path):
    """
    Parses a PDF file and attempts to add Page Number and Section metadata structure.
    """
    if not os.path.exists(pdf_path):
        print(f"Error: {pdf_path} not found.")
        return []
        
    doc = fitz.open(pdf_path)
    documents = []
    
    current_section = "General"
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        
        lines = text.split("\n")
        page_chunks = []
        
        for line in lines:
            line_cleaned = line.strip()
            if not line_cleaned:
                continue
            
            if line_cleaned.upper() == line_cleaned and len(line_cleaned) > 4 and len(line_cleaned) < 60:
                current_section = line_cleaned
            elif line_cleaned.startswith("Clause ") or line_cleaned.startswith("Section ") or line_cleaned.startswith("Article "):
                current_section = line_cleaned
                
            page_chunks.append(line_cleaned)
            
        page_text = "\n".join(page_chunks)
        if page_text.strip():
            metadata = {
                "page": page_num + 1,
                "section": current_section,
                "source": os.path.basename(pdf_path)
            }
            documents.append(Document(page_content=page_text, metadata=metadata))
            
    doc.close()
    return documents

def chunk_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " ", ""],
        length_function=len
    )
    return text_splitter.split_documents(documents)

def process_file_to_db(pdf_path):
    print(f"Processing {pdf_path}...")
    docs = parse_pdf_to_documents(pdf_path)
    if not docs:
        raise ValueError("Failed to parse PDF or PDF is empty.")
        
    print(f"Extracted {len(docs)} pages.")
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks.")
    
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        print("Creating Chroma vector store... this might take a minute.")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=DB_DIR
        )
        print("Vector database built successfully and saved!")
        return True
    except Exception as e:
        print(f"Failed to create vector store: {e}")
        raise e

if __name__ == "__main__":
    PDF_PATH = os.path.join(FILE_DIR, "..", "docs", "TITAN SECURE.pdf")
    process_file_to_db(PDF_PATH)
