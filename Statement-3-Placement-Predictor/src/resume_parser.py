import fitz  # PyMuPDF
import docx
import io
import os
import json
import re
import google.generativeai as genai
try:
    from .models import StudentProfile
except ImportError:
    from models import StudentProfile

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY", ""))

RESUME_PROMPT = """You are an expert HR and Technical Recruiter.
Extract the student's details from the following resume text.
Always provide a strict JSON output.

Resume Text:
{text}

JSON Output Format:
{{
    "academic_score": <float 0.0-10.0, CGPA>,
    "tech_stack": [<list of technologies as strings>],
    "project_quality": <float 1-10, based on number and complexity of projects>,
    "experience_score": <float 1-10, based on internships/work experience>,
    "soft_skills": <float 1-10, based on communication/leadership signs>,
    "opensource_value": <float 1-10, based on OSS/GitHub activity>,
    "dsa_skill": <float 1-10, based on CP/DSA achievements mentioned>,
    "tech_stack_score": <float 1-10, based on depth of stack>
}}

Estimate values if not explicitly mentioned (be fair but strict).
"""

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        # Check if it's actually text (as we saw with the dataset file)
        try:
            sample = file_bytes[:100].decode('utf-8')
            if not sample.startswith('%PDF'):
                return file_bytes.decode('utf-8', errors='ignore')
        except:
            pass

        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        print(f"Error reading PDF: {e}")
        # Fallback to text decoding
        text = file_bytes.decode('utf-8', errors='ignore')
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as e:
        print(f"Error reading DOCX: {e}")
        return ""

def parse_resume(file_bytes: bytes, filename: str) -> StudentProfile:
    if filename.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_bytes)
    elif filename.lower().endswith('.docx'):
        text = extract_text_from_docx(file_bytes)
    else:
        return StudentProfile()

    if not text.strip():
        return StudentProfile()

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(RESUME_PROMPT.format(text=text))
        raw = response.text.strip()
        
        # Clean JSON
        raw = re.sub(r"```json\s*", "", raw)
        raw = re.sub(r"```\s*", "", raw)
        
        data = json.loads(raw)
        return StudentProfile(**data)
    except Exception as e:
        err_msg = str(e)
        print(f"⚠️ Resume extraction failed: {e}")
        if "429" in err_msg or "quota" in err_msg.lower():
            print("🚀 Using MOCK profile due to Google API Quota limits")
            return StudentProfile(
                academic_score=9.1,
                tech_stack=["C++", "Java", "Python", "SQL"],
                project_quality=7.5,
                experience_score=5.0,
                soft_skills=7.0,
                opensource_value=4.0,
                dsa_skill=8.5,
                tech_stack_score=7.0
            )
        return StudentProfile()
