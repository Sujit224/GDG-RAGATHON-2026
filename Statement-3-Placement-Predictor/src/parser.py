from __future__ import annotations

from pathlib import Path
from typing import Callable
import json
import re

from pydantic import BaseModel, Field
from PyPDF2 import PdfReader


class ResumeExtraction(BaseModel):
    cgpa: float | None = Field(default=None)
    tech_stack: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    internships: list[str] = Field(default_factory=list)
    open_source_experience: list[str] = Field(default_factory=list)


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file not found: {path}")

    reader = PdfReader(str(path))
    text_parts: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def _heuristic_resume_parse(resume_text: str) -> ResumeExtraction:
    text = resume_text
    lower = resume_text.lower()

    cgpa_match = re.search(r"\b(?:cgpa|gpa)\s*[:\-]?\s*(\d(?:\.\d{1,2})?)\b", lower)
    cgpa = float(cgpa_match.group(1)) if cgpa_match else None

    known_skills = [
        "python",
        "java",
        "c++",
        "javascript",
        "typescript",
        "react",
        "node.js",
        "sql",
        "mongodb",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "docker",
        "kubernetes",
        "aws",
        "azure",
        "git",
    ]
    tech_stack = []
    for skill in known_skills:
        if skill.lower() in lower:
            tech_stack.append(skill)

    lines = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]
    projects = [line for line in lines if "project" in line.lower()][:5]
    internships = [line for line in lines if "intern" in line.lower()][:5]
    open_source = [
        line
        for line in lines
        if any(keyword in line.lower() for keyword in ["open source", "github", "contributor"])
    ][:5]

    return ResumeExtraction(
        cgpa=cgpa,
        tech_stack=tech_stack,
        projects=projects,
        internships=internships,
        open_source_experience=open_source,
    )


def parse_resume_with_llm_structured_output(
    resume_text: str,
    llm_callable: Callable[[str], str] | None = None,
) -> dict:
    """
    Extract structured resume fields.
    If an LLM callable is provided, it is expected to return strict JSON matching ResumeExtraction.
    """
    system_prompt = (
        "You are a resume information extractor. "
        "Return valid JSON with keys exactly: "
        "cgpa, tech_stack, projects, internships, open_source_experience. "
        "Do not include extra keys."
    )
    user_prompt = f"Resume text:\n{resume_text}\n\nExtract the fields as JSON."

    if llm_callable is not None:
        llm_raw_output = llm_callable(f"{system_prompt}\n\n{user_prompt}")
        parsed = ResumeExtraction.model_validate(json.loads(llm_raw_output))
        return parsed.model_dump()

    heuristic = _heuristic_resume_parse(resume_text)
    return heuristic.model_dump()


def parse_resume_pdf(pdf_path: str | Path, llm_callable: Callable[[str], str] | None = None) -> dict:
    resume_text = extract_text_from_pdf(pdf_path)
    return parse_resume_with_llm_structured_output(resume_text=resume_text, llm_callable=llm_callable)


if __name__ == "__main__":
    sample_resume = Path(__file__).resolve().parents[1] / "data" / "sample_resume.pdf"
    if sample_resume.exists():
        print(json.dumps(parse_resume_pdf(sample_resume), indent=2))
    else:
        print("No sample_resume.pdf found. Import parse_resume_pdf() in your app flow.")
