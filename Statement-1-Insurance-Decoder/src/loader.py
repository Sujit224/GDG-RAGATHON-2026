import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_split_documents(docs_dir):
    """Loads all PDFs from a directory and splits them into chunks."""
    print(f"--- Scanning for PDFs in: {docs_dir} ---")
    
    # Load ALL PDFs in the directory
    loader = PyPDFDirectoryLoader(docs_dir)
    documents = loader.load()
    
    if not documents:
        raise ValueError(f"No PDF files found in {docs_dir}! Please add some.")
        
    print(f"Found {len(documents)} pages across all documents.")
        
    # Split into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)
    
    print(f"Successfully split into {len(chunks)} chunks.")
    return chunks