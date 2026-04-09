from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import chromadb
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from llama_index.core import Document as LlamaDocument
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore


BASE_DIR = Path(__file__).resolve().parents[1]
PDF_PATH = BASE_DIR / "docs" / "TITAN SECURE.pdf"
VECTOR_DB_DIR = BASE_DIR / "vector_db"
COLLECTION_NAME = "insurance_fine_print_decoder"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

SYSTEM_PROMPT = """You are The Fine Print Decoder, an expert insurance policy explainer.

Follow these rules for EVERY answer:
1) Explain in ELI5 language: simple words, short sentences, clear examples.
2) You MUST cite exact references for each key claim:
   - Section number (e.g., "Section 4")
   - Clause number (e.g., "Clause 4.2")
3) If a section/clause cannot be found in retrieved context, say:
   "I could not verify the exact Section/Clause from the provided policy text."
4) Never make up policy details.
5) Format output with:
   - Plain-English Answer
   - Policy Citations
"""


@dataclass
class RetrievalResult:
    question: str
    prompt_for_llm: str
    retrieved_chunks: list[Document]


def load_policy_documents(pdf_path: Path) -> list[Document]:
    if not pdf_path.exists():
        raise FileNotFoundError(f"Policy PDF not found at: {pdf_path}")
    return PyPDFLoader(str(pdf_path)).load()


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_documents(documents)


def build_langchain_vector_store(chunks: list[Document]) -> Chroma:
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(VECTOR_DB_DIR),
    )


def build_llamaindex(chunks: list[Document]) -> VectorStoreIndex:
    chroma_client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
    chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    llama_docs = [
        LlamaDocument(text=doc.page_content, metadata=doc.metadata or {})
        for doc in chunks
    ]
    embed_model = HuggingFaceEmbedding(model_name=EMBEDDING_MODEL)
    return VectorStoreIndex.from_documents(
        llama_docs,
        storage_context=storage_context,
        embed_model=embed_model,
    )


def create_high_stakes_retriever(vector_store: Chroma):
    return vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 6,
            "fetch_k": 30,
            "lambda_mult": 0.2,
        },
    )


def _extract_section_clause(text: str) -> tuple[str | None, str | None]:
    section_match = re.search(r"\bSection\s+([A-Za-z0-9.\-]+)", text, flags=re.IGNORECASE)
    clause_match = re.search(r"\bClause\s+([A-Za-z0-9.\-]+)", text, flags=re.IGNORECASE)
    section = section_match.group(1) if section_match else None
    clause = clause_match.group(1) if clause_match else None
    return section, clause


def build_context_block(retrieved_docs: list[Document]) -> str:
    blocks: list[str] = []
    for idx, doc in enumerate(retrieved_docs, start=1):
        section, clause = _extract_section_clause(doc.page_content)
        meta = doc.metadata or {}
        page = meta.get("page", "unknown")
        blocks.append(
            (
                f"[Chunk {idx}] Page {page}\n"
                f"Detected Section: {section or 'not found'}\n"
                f"Detected Clause: {clause or 'not found'}\n"
                f"Text:\n{doc.page_content}"
            )
        )
    return "\n\n".join(blocks)


def build_eli5_prompt(question: str, context_block: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"User Question:\n{question}\n\n"
        f"Retrieved Policy Context:\n{context_block}\n\n"
        "Generate a concise, accurate answer using only the retrieved policy context."
    )


class FinePrintDecoder:
    def __init__(self) -> None:
        documents = load_policy_documents(PDF_PATH)
        chunks = split_documents(documents)
        self.vector_store = build_langchain_vector_store(chunks)
        self.langchain_retriever = create_high_stakes_retriever(self.vector_store)
        self.llamaindex_index = build_llamaindex(chunks)

    def retrieve(self, question: str) -> RetrievalResult:
        docs = self.langchain_retriever.invoke(question)
        context_block = build_context_block(docs)
        prompt = build_eli5_prompt(question=question, context_block=context_block)
        return RetrievalResult(
            question=question,
            prompt_for_llm=prompt,
            retrieved_chunks=docs,
        )


def demo_query(question: str) -> dict[str, Any]:
    decoder = FinePrintDecoder()
    result = decoder.retrieve(question)
    return {
        "question": result.question,
        "retrieved_chunk_count": len(result.retrieved_chunks),
        "llm_prompt_preview": result.prompt_for_llm[:1200],
    }


if __name__ == "__main__":
    sample_question = "If I am hospitalized after a pre-existing condition flare-up, will my claim be rejected?"
    output = demo_query(sample_question)
    print("Fine Print Decoder initialized.")
    print(f"Question: {output['question']}")
    print(f"Retrieved chunks: {output['retrieved_chunk_count']}")
    print("\nPrompt preview:\n")
    print(output["llm_prompt_preview"])
