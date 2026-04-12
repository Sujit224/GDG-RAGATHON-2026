from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
def process_policy_document(file_path):
 # Load the TITAN SECURE PDF
 loader = PyPDFLoader(file_path)
 pages = loader.load()

 # Split text while preserving metadata for Source Attribution
 text_splitter = RecursiveCharacterTextSplitter(
 chunk_size=500,
 chunk_overlap=50,
 add_start_index=True
 )
 chunks = text_splitter.split_documents(pages)
 return chunks
