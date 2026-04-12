from pydantic import BaseModel, Field
from typing import List


class StudentProfile(BaseModel):
    academic_score: float = Field(default=0.0, ge=0.0, le=10.0)
    tech_stack: List[str] = Field(default_factory=list)
    project_quality: float = Field(default=0.0, ge=0.0, le=10.0)
    experience_score: float = Field(default=0.0, ge=0.0, le=10.0)
    soft_skills: float = Field(default=0.0, ge=0.0, le=10.0)
    opensource_value: float = Field(default=0.0, ge=0.0, le=10.0)
    dsa_skill: float = Field(default=0.0, ge=0.0, le=10.0)
    tech_stack_score: float = Field(default=0.0, ge=0.0, le=10.0)

    def is_complete(self) -> bool:
        return self.academic_score > 0 or len(self.tech_stack) > 0


class ExperienceMatch(BaseModel):
    student_name: str = Field(default="Anonymous Senior")
    company: str = Field(default="Unknown Company")
    role: str = Field(default="Software Engineer")
    tech_stack: List[str] = Field(default_factory=list)
    experience_text: str = Field(default="")
    outcome: str = Field(default="Selected")
    similarity_score: float = Field(default=0.0)


class AnalysisResult(BaseModel):
    profile: StudentProfile
    readiness_score: float = Field(default=0.0, ge=0.0, le=100.0)
    top_experiences: List[ExperienceMatch] = Field(default_factory=list)
