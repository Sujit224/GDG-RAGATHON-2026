import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_classic.chains import RetrievalQA
from langchain_classic.prompts import PromptTemplate

# 1. Configuration & API Setup
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
PDF_PATH = "../docs/TITAN SECURE.pdf"

def build_insurance_bot():
    # 2. Context Loading (Ingestion)
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    # 3. Smart Splitting (Preserving Page Numbers for Bonus)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800, 
        chunk_overlap=100
    )
    chunks = text_splitter.split_documents(docs)

    # 4. Embedding Logic (Using HuggingFace as requested)
    # This runs locally on your CPU/GPU, no API key needed for this part
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # 5. Vector Storage (ChromaDB)
    vector_db = Chroma.from_documents(
        documents=chunks, 
        embedding=embeddings,
        persist_directory="./chroma_db"
    )

    # 6. Hybrid Knowledge Prompt (The "ELI5" + Bonus Requirement)
    template = """
    You are the 'Fine Print Decoder'. Your job is to simplify the provided policy text.
    
    CONTEXT: {context}
    
    USER QUESTION: {question}
    
    STRICT RULES:
    1. Answer using "ELI5" (Explain Like I'm Five) language.
    2. You MUST cite the Page Number and Section if available in the context.
    3. If the context doesn't mention the topic, say you don't know.
    
    RESPONSE FORMAT:
    - SIMPLE EXPLANATION: [Your ELI5 answer]
    - LEGAL SOURCE: [Section Name/Clause Number] from Page [Number]
    """
    
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])

    # 7. RAG Chain with Groq
    llm = ChatGroq(
    api_key=GROQ_API_KEY, 
    model_name="llama-3.3-70b-versatile",  # This is the active, current model
    temperature=0
)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vector_db.as_retriever(search_kwargs={"k": 3}),
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa_chain

# Example Usage:
# bot = build_insurance_bot()
# print(bot.run("Is there a penalty for early cancellation?"))