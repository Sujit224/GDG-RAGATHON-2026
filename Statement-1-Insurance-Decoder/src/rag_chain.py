import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables
load_dotenv()

DB_DIR = os.path.join(os.path.dirname(__file__), "..", "chroma_db")

def get_retriever():
    """Load the ChromaDB and return a retriever."""
    if not os.path.exists(DB_DIR):
        raise FileNotFoundError(f"Chroma DB directory {DB_DIR} not found. Did you run ingest.py?")
        
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    return vector_store.as_retriever(search_kwargs={"k": 5})

def format_docs(docs):
    """Format documents into a single string to include in the context."""
    formatted_texts = []
    for doc in docs:
        page = doc.metadata.get("page", "Unknown")
        section = doc.metadata.get("section", "Unknown")
        text = doc.page_content
        formatted_texts.append(f"[Page: {page} | Section/Clause: {section}]\n{text}")
    return "\n\n---\n\n".join(formatted_texts)

def get_rag_chain():
    """Build the RAG Chain using context injection."""
    retriever = get_retriever()
    # Upgrade to the best available model for legal/insurance reasoning
    llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)

    template = """You are the **Insurance Policy Decoder** 🛡️ — a highly sophisticated, precise, and user-friendly AI.
Your goal is to help users understand complex "Fine Print" from insurance documents with 100% accuracy.

Rules for your response:
1. **Source Citation**: You MUST explicitly cite the Source Section, Clause, and Page number for EVERY point you make.
2. **Double-Response Format**:
   - **Legal Specifics**: First, provide a highly detailed, legally precise answer citing the exact clauses.
   - **ELI5 Summary**: Then, provide a simple "Explain Like I'm Five" summary in a separate section labeled "👶 **Simple Explanation (ELI5)**". Do not use jargon in this part.
3. **Accuracy**: Use ONLY the provided context. If the document doesn't mention the topic, say so clearly.

Context:
{context}

Question:
{question}

Answer (Detailed Analysis + ELI5 Summary):"""
    prompt = ChatPromptTemplate.from_template(template)

    # RAG pipeline
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
