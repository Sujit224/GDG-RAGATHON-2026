import os
import io
from pathlib import Path
 
 
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF resume using pdfplumber."""
    try:
        import pdfplumber
        text_parts = []
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        return "\n".join(text_parts)
    except ImportError:
        raise ImportError("pdfplumber is required for PDF parsing. Run: pip install pdfplumber")
    except Exception as e:
        raise RuntimeError(f"Failed to extract PDF text: {e}")
 
 
def extract_text_from_docx(file_path: str) -> str:
    """Extract text content from a DOCX resume using python-docx."""
    try:
        from docx import Document
        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except ImportError:
        raise ImportError("python-docx is required for DOCX parsing. Run: pip install python-docx")
    except Exception as e:
        raise RuntimeError(f"Failed to extract DOCX text: {e}")
 
 
def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """
    Extract text from uploaded file bytes.
    Supports PDF and DOCX formats.
    Used by the Streamlit UI for file upload.
    """
    import tempfile
    suffix = Path(filename).suffix.lower()
 
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
 
    try:
        if suffix == ".pdf":
            return extract_text_from_pdf(tmp_path)
        elif suffix in (".docx", ".doc"):
            return extract_text_from_docx(tmp_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}. Use PDF or DOCX.")
    finally:
        os.unlink(tmp_path)
 
 
def parse_resume(file_path: str) -> str:
    """
    Parse a resume file (PDF/DOCX) and return raw text.
    Entry point for CLI usage.
    """
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix in (".docx", ".doc"):
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported format: {suffix}")
 
 
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python resume_parser.py <resume.pdf|resume.docx>")
        sys.exit(1)
    text = parse_resume(sys.argv[1])
    print(f"Extracted {len(text)} characters:\n")
    print(text[:500], "..." if len(text) > 500 else "")