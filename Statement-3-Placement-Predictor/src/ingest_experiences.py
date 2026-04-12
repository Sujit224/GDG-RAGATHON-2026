"""
Ingest Interview Experiences into ChromaDB
==========================================
Sources:
  1. INTERVIEW EXPERIENCES.pdf  - Senior interview narratives
  2. placement_dataset.xlsx     - Rich student profiles with text fields

Stores chunked text + metadata into a ChromaDB collection for RAG retrieval.
"""

import os
import re
from pathlib import Path
import pandas as pd
import chromadb

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"

PDF_PATH = DATA_DIR / "INTERVIEW EXPERIENCES.pdf"
XLSX_PATH = DATA_DIR / "placement_dataset.xlsx"

COLLECTION_NAME = "interview_experiences"


def extract_pdf_text(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    from pypdf import PdfReader
    reader = PdfReader(str(pdf_path))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def build_student_experience_docs(df: pd.DataFrame) -> list:
    """
    Build rich experience documents from the placement dataset.
    Each placed student becomes a 'pseudo interview experience'.
    """
    docs = []

    for _, row in df.iterrows():
        placed = str(row.get("placed", "")).strip()
        company = str(row.get("company_placed", "")).strip()
        role = str(row.get("role_offered", "")).strip()

        if placed != "Yes" or company == "Not Placed" or not company or company == "nan":
            continue

        # Build a rich text document from available fields
        parts = []
        parts.append(f"Company: {company}")
        parts.append(f"Role: {role}")

        branch = str(row.get("branch", ""))
        if branch and branch != "nan":
            parts.append(f"Branch: {branch}")

        college = str(row.get("college", ""))
        tier = str(row.get("college_tier", ""))
        if college and college != "nan":
            parts.append(f"College: {college} ({tier})")

        cgpa = row.get("cgpa", 0)
        if cgpa and cgpa > 0:
            parts.append(f"CGPA: {cgpa}")

        tech = str(row.get("tech_stack", ""))
        if tech and tech != "nan":
            parts.append(f"Tech Stack: {tech}")

        domain = str(row.get("domain", ""))
        if domain and domain != "nan":
            parts.append(f"Domain: {domain}")

        projects = str(row.get("projects_description", ""))
        if projects and projects != "nan":
            parts.append(f"Projects: {projects}")

        internships = str(row.get("internship_details", ""))
        if internships and internships != "nan":
            parts.append(f"Internships: {internships}")

        opensource = str(row.get("opensource_details", ""))
        if opensource and opensource != "nan":
            parts.append(f"Open Source: {opensource}")

        pkg = row.get("package_lpa", 0)
        if pkg and pkg > 0:
            parts.append(f"Package: {pkg} LPA")

        readiness = row.get("readiness_score", 0)
        if readiness and readiness > 0:
            parts.append(f"Readiness Score: {readiness}")

        doc_text = " | ".join(parts)

        metadata = {
            "source": "placement_dataset",
            "company": company,
            "role": role,
            "branch": branch if branch != "nan" else "",
            "domain": domain if domain != "nan" else "",
            "tech_stack": tech if tech != "nan" else "",
            "package_lpa": float(pkg) if pkg else 0.0,
            "cgpa": float(cgpa) if cgpa else 0.0,
        }

        docs.append({"text": doc_text, "metadata": metadata})

    return docs


def ingest():
    """Main ingestion pipeline."""
    print("=" * 60)
    print("  Interview Experience Ingestion Pipeline")
    print("=" * 60)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    # Delete existing collection to re-ingest fresh
    try:
        client.delete_collection(COLLECTION_NAME)
        print("[*] Deleted existing collection for fresh ingestion")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Senior interview experiences and placement profiles"},
    )

    all_ids = []
    all_docs = []
    all_metas = []
    idx = 0

    # ── 1. PDF Interview Experiences ──────────────────────────────────
    if PDF_PATH.exists():
        print(f"\n[1/2] Processing PDF: {PDF_PATH.name}")
        pdf_text = extract_pdf_text(PDF_PATH)
        print(f"      Extracted {len(pdf_text)} characters")

        chunks = chunk_text(pdf_text, chunk_size=600, overlap=100)
        print(f"      Created {len(chunks)} chunks")

        for chunk in chunks:
            all_ids.append(f"pdf_{idx}")
            all_docs.append(chunk)
            all_metas.append({
                "source": "interview_experiences_pdf",
                "company": "",
                "role": "",
                "branch": "",
                "domain": "",
                "tech_stack": "",
                "package_lpa": 0.0,
                "cgpa": 0.0,
            })
            idx += 1
    else:
        print(f"\n[1/2] PDF not found at {PDF_PATH}, skipping...")

    # ── 2. XLSX Placement Dataset ─────────────────────────────────────
    if XLSX_PATH.exists():
        print(f"\n[2/2] Processing XLSX: {XLSX_PATH.name}")
        df = pd.read_excel(str(XLSX_PATH))
        print(f"      Loaded {len(df)} student records")

        student_docs = build_student_experience_docs(df)
        print(f"      Built {len(student_docs)} placed-student experience docs")

        for doc in student_docs:
            all_ids.append(f"student_{idx}")
            all_docs.append(doc["text"])
            all_metas.append(doc["metadata"])
            idx += 1
    else:
        print(f"\n[2/2] XLSX not found at {XLSX_PATH}, skipping...")

    # ── 3. Batch upsert ──────────────────────────────────────────────
    if all_docs:
        print(f"\n[*] Upserting {len(all_docs)} documents into ChromaDB...")
        batch_size = 100
        for i in range(0, len(all_docs), batch_size):
            end = min(i + batch_size, len(all_docs))
            collection.add(
                ids=all_ids[i:end],
                documents=all_docs[i:end],
                metadatas=all_metas[i:end],
            )
            print(f"    Batch {i}-{end} done")

        print(f"\n[OK] Total documents ingested: {collection.count()}")
    else:
        print("\n[WARN] No documents to ingest!")

    print("=" * 60)


if __name__ == "__main__":
    ingest()
