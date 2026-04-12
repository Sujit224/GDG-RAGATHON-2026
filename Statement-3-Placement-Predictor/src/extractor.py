import os
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pypdf import PdfReader
import docx

class StudentProfile(BaseModel):
    cgpa: float = Field(description="Cumulative Grade Point Average")
    tech_stack: List[str] = Field(description="List of programming languages and frameworks")
    projects_count: int = Field(description="Number of significant projects")
    internships_count: int = Field(description="Number of internships completed")
    communication_score: int = Field(description="Communication skill level from 1 to 10")
    opensource_experience: bool = Field(description="Whether the student has open source contributions")

class ProfileExtractor:
    def __init__(self):
        self.llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
        self.parser = PydanticOutputParser(pydantic_object=StudentProfile)
        
        self.prompt = PromptTemplate(
            template="Extract the following student profile details from the text and return ONLY a valid JSON object.\n{format_instructions}\nInput Text: {text}\n\nReturn only the JSON, no other text:",
            input_variables=["text"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )

    def extract_from_text(self, text: str) -> StudentProfile:
        """Extracts structured JSON from raw chat text or resume content."""
        chain = self.prompt | self.llm | self.parser
        try:
            return chain.invoke({"text": text})
        except Exception:
            return self._fallback_profile(text)

    def _fallback_profile(self, text: str) -> StudentProfile:
        """Fallback profile extraction when the LLM output cannot be parsed."""
        cgpa = self._extract_first_float(text, min_value=0.0, max_value=10.0, default=6.5)
        communication_score = self._extract_first_int(text, min_value=1, max_value=10, default=6)
        projects_count = self._extract_first_int(text, keywords=["project"], default=1)
        internships_count = self._extract_first_int(text, keywords=["internship"], default=0)
        opensource_experience = self._detect_opensource(text)
        tech_stack = self._extract_tech_stack(text)

        return StudentProfile(
            cgpa=cgpa,
            tech_stack=tech_stack,
            projects_count=projects_count,
            internships_count=internships_count,
            communication_score=communication_score,
            opensource_experience=opensource_experience
        )

    def _extract_first_float(self, text: str, min_value: float = 0.0, max_value: float = 10.0, default: float = 0.0) -> float:
        import re
        matches = re.findall(r"\b([0-9]+(?:\.[0-9]+)?)\b", text)
        for match in matches:
            try:
                value = float(match)
            except ValueError:
                continue
            if min_value <= value <= max_value:
                return value
        return default

    def _extract_first_int(self, text: str, min_value: int = 0, max_value: int = 100, keywords: list[str] | None = None, default: int = 0) -> int:
        import re
        if keywords:
            for keyword in keywords:
                pattern = rf"{keyword}s?\D{{0,10}}([0-9]+)"
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    value = int(match.group(1))
                    return max(min(value, max_value), min_value)
        matches = re.findall(r"\b([0-9]{1,2})\b", text)
        for match in matches:
            value = int(match)
            if min_value <= value <= max_value:
                return value
        return default

    def _extract_tech_stack(self, text: str) -> list[str]:
        tech_keywords = [
            "Python", "Java", "C++", "C#", "JavaScript", "TypeScript", "SQL", "HTML", "CSS",
            "React", "Node.js", "Django", "Flask", "Swift", "Kotlin", "AWS", "Azure", "Docker",
            "Kubernetes", "Linux", "Git", "TensorFlow", "PyTorch", "MongoDB", "PostgreSQL"
        ]
        found = []
        for tech in tech_keywords:
            if tech.lower() in text.lower():
                found.append(tech)
        return found or ["Python"]

    def _detect_opensource(self, text: str) -> bool:
        keywords = ["open source", "github", "contribution", "contributed", "oss"]
        return any(keyword in text.lower() for keyword in keywords)

    def parse_resume(self, file_path: str) -> str:
        """Bonus: Extracts text from PDF or DOCX resumes."""
        if file_path.lower().endswith('.pdf'):
            return self._extract_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            return self._extract_from_docx(file_path)
        else:
            raise ValueError("Only PDF and DOCX files are supported")

    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text

    def get_structured_profile(self, input_data: str, is_file: bool = False) -> StudentProfile:
        content = self.parse_resume(input_data) if is_file else input_data
        return self.extract_from_text(content)