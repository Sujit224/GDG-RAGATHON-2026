from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


@dataclass
class SeniorExperience:
    candidate_name: str
    company: str
    role: str
    tech_stack: list[str]
    summary: str


DUMMY_EXPERIENCES: list[SeniorExperience] = [
    SeniorExperience(
        candidate_name="Aarav Singh",
        company="Amazon",
        role="SDE-1",
        tech_stack=["python", "aws", "docker", "sql"],
        summary="Focused on DSA rounds and backend design with Python microservices on AWS.",
    ),
    SeniorExperience(
        candidate_name="Sana Khan",
        company="Google",
        role="Software Engineer",
        tech_stack=["c++", "system design", "distributed systems", "go"],
        summary="Prepared deep problem-solving and scalable systems design interview stories.",
    ),
    SeniorExperience(
        candidate_name="Vivek Verma",
        company="Microsoft",
        role="Software Engineer",
        tech_stack=["python", "machine learning", "pytorch", "sql"],
        summary="Built ML portfolio projects and discussed practical model deployment tradeoffs.",
    ),
    SeniorExperience(
        candidate_name="Nidhi Gupta",
        company="Flipkart",
        role="Data Scientist",
        tech_stack=["python", "tensorflow", "scikit-learn", "mlops"],
        summary="Cracked ML interviews by combining statistics fundamentals with project narratives.",
    ),
    SeniorExperience(
        candidate_name="Rohan Mehta",
        company="Zomato",
        role="Backend Engineer",
        tech_stack=["java", "spring boot", "mysql", "kafka"],
        summary="Shared backend interview prep path focusing on APIs, DB design, and message queues.",
    ),
]


def _stack_to_text(tech_stack: list[str]) -> str:
    return ", ".join(skill.strip().lower() for skill in tech_stack if skill and skill.strip())


def find_top_experience_matches(user_tech_stack: list[str], top_k: int = 3) -> list[dict[str, Any]]:
    if not user_tech_stack:
        raise ValueError("user_tech_stack must contain at least one skill.")

    model = SentenceTransformer(EMBEDDING_MODEL)
    query_text = _stack_to_text(user_tech_stack)
    corpus_texts = [_stack_to_text(exp.tech_stack) for exp in DUMMY_EXPERIENCES]

    query_vector = model.encode([query_text])
    corpus_vectors = model.encode(corpus_texts)
    similarity_scores = cosine_similarity(query_vector, corpus_vectors)[0]

    top_indices = np.argsort(similarity_scores)[::-1][:top_k]
    matches: list[dict[str, Any]] = []
    for index in top_indices:
        exp = DUMMY_EXPERIENCES[int(index)]
        matches.append(
            {
                "similarity": round(float(similarity_scores[index]), 4),
                "candidate_name": exp.candidate_name,
                "company": exp.company,
                "role": exp.role,
                "tech_stack": exp.tech_stack,
                "summary": exp.summary,
            }
        )
    return matches


if __name__ == "__main__":
    sample_stack = ["python", "sql", "aws", "docker"]
    top_matches = find_top_experience_matches(sample_stack, top_k=3)
    for rank, match in enumerate(top_matches, start=1):
        print(f"{rank}. {match['candidate_name']} ({match['company']}) - score={match['similarity']}")
