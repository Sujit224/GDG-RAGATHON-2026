from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


from dotenv import load_dotenv
load_dotenv()

embed = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    # dimensions = 64
)




data = PyPDFLoader("Statement-1-Insurance-Decoder/docs/TITAN SECURE_removed.pdf") 
docs = data.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(docs)

vectorstore = Chroma.from_documents(
    documents= chunks,
    embedding= embed, 
    persist_directory="Chroma_DB"
)
