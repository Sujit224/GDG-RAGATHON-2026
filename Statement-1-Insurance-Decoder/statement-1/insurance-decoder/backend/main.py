import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Optional

load_dotenv()

app = FastAPI(title="Insurance Decoder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
FAISS_INDEX_PATH = "faiss_index"

# Global state to keep track of the vector store in memory (simple for hackathon)
vectorstore = None
retriever = None

class QueryModel(BaseModel):
    query: str

class AskResponse(BaseModel):
    explanation: str
    highlight: str
    is_covered: str # "✅ Covered", "❌ Not Covered", "⚠️ Conditions"

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vectorstore, retriever
    
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        # Load and parse PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)
        
        # Embed and store
        # Embeddings run locally
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(chunks, embeddings)
        vectorstore.save_local(FAISS_INDEX_PATH)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
        
        return {"message": "PDF uploaded and processed successfully", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=AskResponse)
async def ask_question(query_data: QueryModel):
    global vectorstore, retriever
    
    # Try to load vectorstore if it's not in memory
    if vectorstore is None:
        try:
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            if os.path.exists(FAISS_INDEX_PATH):
                vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            else:
                raise HTTPException(status_code=400, detail="No document processed yet. Please upload a PDF first.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading vectorstore: {str(e)}")
            
    try:
        groq_api_key = os.getenv("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")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not set")
            
        print("GROQ_API_KEY:", "***" if groq_api_key else "None") # Redacted for safety in logs
        print("Vectorstore initialized:", vectorstore is not None)
            
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.1-8b-instant",
            temperature=0
        )
        
        # Define JSON parser
        parser = JsonOutputParser(pydantic_object=AskResponse)
        
        from langchain_classic.chains import RetrievalQA
        from langchain_core.prompts import PromptTemplate
        
        prompt_template = """You are an expert insurance policy interpreter. Your job is to help users understand their insurance coverage based ONLY on the provided document context.
            
You MUST return your answer in valid JSON format.
You MUST extract the answer strictly from the document. If it is NOT in the document, state that it is not found.
You MUST simplify the legal language so anyone can understand it (e.g., "MRI requires prior authorization" -> "You must take approval before MRI, otherwise you pay extra.").

Your JSON structure MUST EXACTLY match this:
{{
    "explanation": "A simple, human-friendly explanation of the answer based on the context.",
    "highlight": "A short 1-5 word keyword or key phrase summarizing the condition/coverage.",
    "is_covered": "Must be exactly one of these strings: '✅ Covered', '❌ Not Covered', or '⚠️ Conditions'"
}}

Rules for is_covered:
- If the document explicitly states it is covered without major restrictions, use '✅ Covered'.
- If the document explicitly states it is excluded or not covered, use '❌ Not Covered'.
- If it is covered but requires prior authorization, has deductibles, limits, or specific conditions, use '⚠️ Conditions'.

Context:
{context}

Question: {question}"""
        
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["context", "question"]
        )
        
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": prompt, "document_variable_name": "context"}
        )
        
        try:
            result = qa.run(query_data.query)
            try:
                import json
                parsed_answer = json.loads(result)
                return AskResponse(**parsed_answer)
            except Exception as parse_e:
                print(f"Error parsing JSON: {parse_e}\nRaw output: {result}")
                return AskResponse(
                    explanation=result,
                    highlight="Answer",
                    is_covered="⚠️ Conditions"
                )
        except Exception as e:
            return AskResponse(
                explanation=f"Error executing QA chain: {str(e)}",
                highlight="Error",
                is_covered="❌ Not Covered"
            )
        
    except Exception as e:
        print(f"Error answering question: {e}")
        # Fallback if parsing fails
        return AskResponse(
            explanation=f"Error processing answer: {str(e)}",
            highlight="Error",
            is_covered="❌ Not Covered"
        )

# Risk analyzer endpoint
class RiskScenario(BaseModel):
    scenario: str

@app.post("/analyze-risk", response_model=AskResponse)
async def analyze_risk(data: RiskScenario):
    # Reuse ask logic but format query differently
    query = f"Analyze this scenario based on the policy and determine coverage, risk, and conditions: {data.scenario}"
    return await ask_question(QueryModel(query=query))

@app.get("/")
def read_root():
    return {"status": "Insurance Decoder API is running"}
