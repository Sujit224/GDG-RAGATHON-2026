import fitz  # PyMuPDF
import re

def parse_interview_experiences(pdf_path: str) -> list[dict]:
    """
    Returns a list of dicts:
    {
      "id": int,
      "text": str,          # full experience text
      "company": str,       # extracted if possible
      "tech_stack": list[str],  # keywords extracted
      "raw_chunk": str
    }
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    
    # We will split on some common patterns or double newlines depending on structure.
    # A generic approach: split by typical headers like "Experience", or just large chunks.
    # Given we do not know the exact structure, splitting by "\n\n\n" or simple pagination might help.
    # Let's split by simple heuristic and extract any company names and tech stacks.
    chunks = re.split(r'Experience \d+|Interview Experience|Candidate:|Name:', full_text)
    
    # Filter empty chunks
    chunks = [c.strip() for c in chunks if len(c.strip()) > 50]
    
    results = []
    
    tech_keywords = ['java', 'python', 'c++', 'react', 'node', 'express', 'sql', 'mongodb', 'aws', 'docker', 'machine learning', 'data structures', 'algorithms']
    
    for idx, chunk in enumerate(chunks):
        company = "Unknown"
        # Extract potential company name (e.g., Company: Amazon)
        company_match = re.search(r'(?i)Company[:\s]+(\w+)', chunk)
        if company_match:
            company = company_match.group(1)
        
        # Tech stack
        tech = set()
        for tk in tech_keywords:
            if tk in chunk.lower():
                tech.add(tk)
            
        results.append({
            "id": idx + 1,
            "text": chunk,
            "company": company,
            "tech_stack": list(tech),
            "raw_chunk": chunk
        })
        
    return results
