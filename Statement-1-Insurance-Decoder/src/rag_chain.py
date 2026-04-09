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
    llm = ChatGroq(model_name="llama-3.1-8b-instant", temperature=0)

    template = """You are a highly helpful and precise AI bot designed to extract and convey information from complex documents.
The user is asking a question about the policy document.
Use the following pieces of retrieved context to answer the user's question.

RULES:
1. You must answer ONLY using the provided context. If you don't know the answer, say "I don't have enough information in the policy documents to answer this."
2. Provide a detailed and comprehensive answer that thoroughly addresses the user's question. Include all relevant information, conditions, and coverage details found in the context.
3. Do not include extra unnecessary information, generalizations, or conversational fluff that is not directly related to answering the specific question.
4. **CRITICAL REQUIREMENT (Source Attribution)**: You MUST explicitly cite the exact Source Section/Clause number and Page number for EVERY point or answer you give, referencing the provided metadata tags from the context. Do not invent section numbers.

Context:
{context}

Question:
{question}

Answer (Detailed and highly relevant, with precise Section and Page citations):"""
    prompt = ChatPromptTemplate.from_template(template)

    # RAG pipeline
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain
