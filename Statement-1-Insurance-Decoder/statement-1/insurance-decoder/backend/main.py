import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
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
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=500, detail="OpenAI API Key not set.")
            
        embeddings = OpenAIEmbeddings()
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
            embeddings = OpenAIEmbeddings()
            if os.path.exists(FAISS_INDEX_PATH):
                vectorstore = FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
                retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            else:
                raise HTTPException(status_code=400, detail="No document processed yet. Please upload a PDF first.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error loading vectorstore: {str(e)}")
            
    try:
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        # Define JSON parser
        parser = JsonOutputParser(pydantic_object=AskResponse)
        
        # Prompt: Answer ONLY from document, simplify legal language, output JSON.
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert insurance policy interpreter. Your job is to help users understand their insurance coverage based ONLY on the provided document context.
            
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
{context}"""),
            ("human", "{input}\n\nFormat instructions: {format_instructions}")
        ])
        
        # Use LCEL instead of legacy chains
        from langchain_core.runnables import RunnablePassthrough
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
            
        custom_chain = (
            {
                "context": retriever | format_docs, 
                "input": RunnablePassthrough(),
                "format_instructions": lambda _: parser.get_format_instructions()
            }
            | prompt
            | llm
            | parser
        )
        
        parsed_answer = custom_chain.invoke(query_data.query)
        
        return AskResponse(**parsed_answer)
        
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
