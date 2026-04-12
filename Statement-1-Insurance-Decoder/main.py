import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Silent warnings
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
load_dotenv()

class InsuranceDecoder:
    def __init__(self, model_name="llama-3.1-8b-instant", pdf_path="docs/TITAN SECURE.pdf"):
        self.pdf_path = pdf_path
        self.api_key = os.getenv("GROQ_API_KEY")
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY missing in .env file")

        self.llm = ChatGroq(model=model_name, api_key=self.api_key, temperature=0)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vectorstore = None

    def ingest_document(self):
        if not os.path.exists(self.pdf_path):
            print(f"Error: File not found at {self.pdf_path}")
            sys.exit(1)

        loader = PyPDFLoader(self.pdf_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)

        self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        return self.vectorstore.as_retriever(search_kwargs={"k": 3})

    def get_chain(self, retriever):
        template = """
        You are a professional Insurance Assistant. Use the following context to answer the user's question accurately.
        If the answer is not in the context, state that you don't have enough information.

        Context:
        {context}

        Question: {question}
        
        Answer professionally:"""
        
        prompt = ChatPromptTemplate.from_template(template)

        return (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query):
        print(f"\n[Processing] Analyzing document for: '{query}'...")
        retriever = self.ingest_document()
        chain = self.get_chain(retriever)
        return chain.invoke(query)

if __name__ == "__main__":
    # Execution
    decoder = InsuranceDecoder()
    try:
        user_query = "Does skydiving injury get covered?"
        response = decoder.ask(user_query)
        
        print("-" * 30)
        print(f"QUERY: {user_query}")
        print(f"RESPONSE: {response}")
        print("-" * 30)
    except Exception as e:
        print(f"An error occurred: {e}")
