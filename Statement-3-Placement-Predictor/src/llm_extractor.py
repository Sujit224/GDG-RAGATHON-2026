import os
import fitz  # PyMuPDF
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
import json

class StudentProfile(BaseModel):
    Academic_Score: int = Field(description="Score from 1 to 10 evaluating the student's academic performance based on CGPA and grades.")
    DSA_Skill: int = Field(description="Score from 1 to 10 evaluating the student's knowledge of Data Structures and Algorithms.")
    Project_Quality: int = Field(description="Score from 1 to 10 evaluating the complexity and impact of the student's projects.")
    Experience_Score: int = Field(description="Score from 1 to 10 evaluating the student's internships or professional experience.")
    OpenSource_Value: int = Field(description="Score from 1 to 10 evaluating the student's open source contributions or hackathons.")
    Soft_Skills: int = Field(description="Score from 1 to 10 evaluating the student's communication and teamwork skills.")
    Tech_Stack_Score: int = Field(description="Score from 1 to 10 evaluating the breadth and depth of the student's technology stack/tools.")
    Missing_Info: str = Field(description="A brief sentence detailing any crucially missing info (e.g. 'I still need to know your CGPA and DSA skills'), or empty string if all looks good.")
    Summary: str = Field(description="A 2-3 sentence summary of the student's profile.")

def extract_profile_from_text(context_text: str) -> dict:
    """
    Uses Gemini to extract the 7 feature scores from a text.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment. Please set it in the .env file.")
    
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert tech recruiter and placement mentor. 
    Review the following context about a student (from chat or resume) and extract the requested fields. 
    Score each aspect from 1 to 10 based on the information provided.
    If information is absolutely missing, make a conservative best guess (e.g., 3-5) but clearly specify what is missing in the Missing_Info field so the chatbot can ask the user later.
    Be objective and fair. 
    
    Student Context:
    {context_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=StudentProfile,
            temperature=0.2
        ),
    )
    
    return json.loads(response.text)

def parse_pdf_resume(file_path: str) -> str:
    """Read text from a PDF resume"""
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    return text
