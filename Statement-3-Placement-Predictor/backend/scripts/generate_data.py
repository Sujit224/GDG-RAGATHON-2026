"""
STEP 1: Realistic Placement Dataset Generator
Generates 300 rows with balanced distribution across weak / average / strong profiles.
"""

import numpy as np
import pandas as pd
import random

np.random.seed(42)
random.seed(42)

TECH_STACKS = {
    "strong":  ["MERN", "AI/ML", "Django+React", "FastAPI", "Flutter", "DevOps", "Spring Boot"],
    "medium":  ["React", "Node.js", "Python", "Java", "SQL", "Firebase"],
    "weak":    ["HTML/CSS", "MS Office", "Scratch", "Basic Python", "WordPress"],
}

def sample_tech_stack(tier: str) -> list:
    pool = TECH_STACKS[tier]
    n = random.randint(1, 3)
    return random.sample(pool, min(n, len(pool)))

def build_realistic_profile(profile_type: str) -> dict:
    if profile_type == "weak":
        cgpa            = round(np.random.uniform(4.0, 6.5), 2)
        projects        = random.randint(0, 2)
        internships     = random.randint(0, 1)
        communication   = round(np.random.uniform(2.0, 6.0), 1)
        open_source     = random.choices([0, 1], weights=[0.85, 0.15])[0]
        tech_stack      = sample_tech_stack(random.choices(["weak", "medium"], weights=[0.6, 0.4])[0])

    elif profile_type == "medium":
        cgpa            = round(np.random.uniform(6.5, 8.5), 2)
        projects        = random.randint(1, 4)
        internships     = random.randint(0, 2)
        communication   = round(np.random.uniform(5.0, 8.0), 1)
        open_source     = random.choices([0, 1], weights=[0.55, 0.45])[0]
        tech_stack      = sample_tech_stack(random.choices(["weak", "medium", "strong"], weights=[0.2, 0.5, 0.3])[0])

    else:  # strong
        cgpa            = round(np.random.uniform(8.0, 10.0), 2)
        projects        = random.randint(3, 7)
        internships     = random.randint(1, 4)
        communication   = round(np.random.uniform(7.0, 10.0), 1)
        open_source     = random.choices([0, 1], weights=[0.25, 0.75])[0]
        tech_stack      = sample_tech_stack(random.choices(["medium", "strong"], weights=[0.3, 0.7])[0])

    return {
        "cgpa":           cgpa,
        "projects":       projects,
        "internships":    internships,
        "communication":  communication,
        "open_source":    open_source,
        "tech_stack":     "|".join(tech_stack),
    }

def compute_target_score(row: dict) -> float:
    """Compute a realistic Readiness_Score using calibrated domain logic."""
    cgpa          = row["cgpa"]
    projects      = row["projects"]
    internships   = row["internships"]
    communication = row["communication"]
    open_source   = row["open_source"]
    tech_stack    = row["tech_stack"].split("|")

    # --- Base Weighted Score ---
    score  = (cgpa / 10.0)           * 30   # CGPA contributes 30%
    score += (min(projects, 5) / 5.0) * 20  # Projects (capped at 5) → 20%
    score += (min(internships, 3) / 3.0) * 20  # Internships (capped at 3) → 20%
    score += (communication / 10.0)  * 15   # Communication → 15%
    score += open_source              * 5    # Open source → 5%
    # Tech stack scoring
    strong_tech = set(TECH_STACKS["strong"])
    medium_tech = set(TECH_STACKS["medium"])
    ts_score = 0
    for t in tech_stack:
        if t in strong_tech:
            ts_score += 3
        elif t in medium_tech:
            ts_score += 1.5
        else:
            ts_score += 0.5
    score += min(ts_score / 9.0, 1.0) * 10  # Tech stack → 10%

    # --- Boosts & Caps ---
    if cgpa >= 9.0:
        score += 8
    elif cgpa >= 8.0:
        score += 4

    if internships >= 2:
        score += 7
    elif internships == 0:
        score -= 5

    if projects > 3:
        score += 3
    elif projects <= 1:
        score -= 3

    if communication >= 8:
        score += 3
    elif communication < 5:
        score -= 5

    if open_source == 1:
        score += 4

    # Hard caps
    if cgpa < 6.0:
        score = min(score, 60)
    if projects == 0:
        score = min(score, 55)

    # Add small realistic noise
    noise = np.random.normal(0, 2.5)
    score += noise

    return round(max(5.0, min(100.0, score)), 2)

# --- Generate Dataset ---
profiles = (
    [("weak",   build_realistic_profile("weak"))   for _ in range(90)]  +  # 30%
    [("medium", build_realistic_profile("medium")) for _ in range(130)] +  # ~43%
    [("strong", build_realistic_profile("strong")) for _ in range(80)]     # ~27%
)

random.shuffle(profiles)

records = []
for tier, row in profiles:
    row["readiness_score"] = compute_target_score(row)
    records.append(row)

df = pd.DataFrame(records)
print(df["readiness_score"].describe())
print("\nSample records:")
print(df.head(10).to_string())

output_path = "data/realistic_placement_data.csv"
df.to_csv(output_path, index=False)
print(f"\nDataset saved to {output_path} ({len(df)} rows)")
