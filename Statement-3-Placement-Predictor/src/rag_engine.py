import os
import re
import json
import faiss
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
try:
    from .models import StudentProfile, ExperienceMatch
except ImportError:
    from models import StudentProfile, ExperienceMatch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "INTERVIEW EXPERIENCES.pdf")
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.bin")
METADATA_PATH = os.path.join(BASE_DIR, "data", "senior_experiences_metadata.json")

class ExperienceRAG:
    def __init__(self):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.experiences = []
        self._initialize()

    def _initialize(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "r") as f:
                self.experiences = json.load(f)
        else:
            self.build_index()

    def build_index(self):
        if not os.path.exists(DATA_PATH):
            print(f"⚠️ Interview experiences not found at {DATA_PATH}")
            return

        # Read as text since it's actually a txt file with .pdf extension
        with open(DATA_PATH, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Split by "1. ", "2. ", etc. at the start of lines
        chunks = re.split(r'\n(?=\d+\.\s+)', content)
        
        parsed_experiences = []
        vectors = []

        for chunk in chunks:
            if not chunk.strip():
                continue
                
            # Parse title, metadata, skills
            lines = chunk.strip().split('\n')
            title = lines[0].strip()
            
            company = "Unknown"
            role = "Software Engineer"
            skills = []
            
            # Use regex to extract details from the "Metadata:" and "Skills:" lines
            for line in lines:
                if line.startswith("Metadata:"):
                    parts = line.replace("Metadata:", "").split("|")
                    if len(parts) >= 1: company = parts[0].strip()
                    if len(parts) >= 2: role = parts[1].strip()
                elif line.startswith("Skills:"):
                    skills = [s.strip() for s in line.replace("Skills:", "").split(",")]
            
            exp_data = {
                "student_name": "Senior Alumnus",
                "company": company,
                "role": role,
                "tech_stack": skills,
                "experience_text": chunk.strip(),
                "outcome": "Selected"
            }
            
            parsed_experiences.append(exp_data)
            # Encode skills and title for matching
            vectors.append(self.encoder.encode(f"{company} {role} {' '.join(skills)} {chunk[:200]}"))

        if vectors:
            vectors = np.array(vectors).astype('float32')
            self.index = faiss.IndexFlatL2(vectors.shape[1])
            self.index.add(vectors)
            self.experiences = parsed_experiences
            
            faiss.write_index(self.index, INDEX_PATH)
            with open(METADATA_PATH, "w") as f:
                json.dump(self.experiences, f)
            print(f"✅ RAG Index built with {len(parsed_experiences)} experiences.")

    def get_top_matches(self, profile: StudentProfile, k: int = 3) -> List[ExperienceMatch]:
        if not self.index or not self.experiences:
            return []

        query = f"{' '.join(profile.tech_stack)}"
        query_vector = self.encoder.encode([query]).astype('float32')
        
        distances, indices = self.index.search(query_vector, k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.experiences):
                exp = self.experiences[idx]
                sim_score = float(max(0, 100 - (distances[0][i] * 50))) # Heuristic similarity score
                results.append(ExperienceMatch(
                    student_name=exp["student_name"],
                    company=exp["company"],
                    role=exp["role"],
                    tech_stack=exp["tech_stack"],
                    experience_text=exp["experience_text"],
                    outcome=exp["outcome"],
                    similarity_score=round(sim_score, 2)
                ))
        
        return results

rag_engine = ExperienceRAG()
