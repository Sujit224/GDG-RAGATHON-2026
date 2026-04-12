import os
from dotenv import load_dotenv
load_dotenv()

from src.utils.parser import extract_text_from_pdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def create_db():
    text = extract_text_from_pdf("data/INTERVIEW EXPERIENCES.pdf")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100
    )

    chunks = splitter.split_text(text)

    db = Chroma.from_texts(
        texts=chunks,
        embedding=HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        ),
        persist_directory="db"
    )

    db.persist()
    print("✅ Vector DB created (FREE embeddings)!")

if __name__ == "__main__":
    create_db()