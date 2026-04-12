from fastapi import FastAPI, UploadFile, File
from src.llm.extractor import extract_profile
from src.ml.model import predict_score
from src.rag.retriever import get_interviews
from src.llm.explainer import generate_explanation
from src.utils.parser import extract_text_from_pdf
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# 🧠 HELPER FUNCTIONS
# =====================================================

def get_level(score):
    if score < 50:
        return "Low readiness"
    elif score < 75:
        return "Moderate readiness"
    else:
        return "High readiness"


def suggest_companies(score):
    if score > 80:
        return ["Google", "Amazon", "Microsoft"]
    elif score > 60:
        return ["Flipkart", "Goldman Sachs", "Adobe"]
    else:
        return ["TCS", "Infosys", "Wipro"]


def get_weaknesses(profile):
    weaknesses = []

    if profile["projects"] < 2:
        weaknesses.append("Low project count")

    if profile["experience"] < 1:
        weaknesses.append("No internships")

    if profile["dsa"] < 5:
        weaknesses.append("Weak DSA")

    if not weaknesses:
        weaknesses.append("Need stronger DSA consistency")

    return weaknesses


# =====================================================
# 🚀 INTELLIGENCE LAYER
# =====================================================

def adjust_for_role(profile, role):
    if role == "ML":
        if "ML" in profile["skills"]:
            profile["tech_stack"] += 2

    if role == "SDE":
        if profile["dsa"] >= 7:
            profile["dsa"] += 1

    return profile


def get_confidence(profile):
    return min(100, (
        profile["projects"] * 10 +
        profile["experience"] * 15 +
        len(profile["skills"]) * 5
    ))


def classify_user(profile):
    if profile["projects"] <= 1:
        return "Beginner"
    elif profile["experience"] >= 2:
        return "Advanced"
    else:
        return "Intermediate"


def skill_gap(profile):
    gaps = []

    if "SQL" not in profile["skills"]:
        gaps.append("SQL")

    if profile["dsa"] < 7:
        gaps.append("DSA")

    if profile["projects"] < 3:
        gaps.append("Real-world Projects")

    return gaps


def roadmap(profile):
    steps = []

    if profile["dsa"] < 7:
        steps.append("Solve 300+ DSA problems")

    if profile["projects"] < 3:
        steps.append("Build 2 advanced projects")

    if profile["experience"] < 2:
        steps.append("Get internship or open-source experience")

    steps.append("Prepare system design")

    return steps


def apply_boost(profile, score):
    boost = 0

    if profile["academic_score"] >= 8.5:
        boost += 10

    if profile["projects"] >= 3:
        boost += 8

    if profile["experience"] >= 2:
        boost += 10

    if len(profile["skills"]) >= 5:
        boost += 7

    if profile["dsa"] >= 7:
        boost += 8

    return min(100, score + boost)


# =====================================================
# 🌐 ROUTES
# =====================================================

@app.get("/")
def home():
    return {"message": "Placement Predictor running 🚀"}


@app.post("/predict")
def predict(data: dict):
    text = data["text"]
    role = data.get("role", "SDE")

    profile = extract_profile(text)
    profile = adjust_for_role(profile, role)

    score = predict_score(profile)
    score = apply_boost(profile, score)

    interviews = get_interviews(profile)
    explanation = generate_explanation(profile, score, interviews, role=role)

    level = get_level(score)
    companies = suggest_companies(score)
    weaknesses = get_weaknesses(profile)

    confidence = get_confidence(profile)
    user_type = classify_user(profile)
    gaps = skill_gap(profile)
    plan = roadmap(profile)

    return {
        "profile": profile,
        "score": score,
        "level": level,
        "profile_type": user_type,
        "confidence": confidence,
        "skill_gaps": gaps,
        "roadmap": plan,
        "recommended_companies": companies,
        "weaknesses": weaknesses,
        "interviews": interviews,
        "analysis": explanation
    }


@app.post("/upload-resume")
def upload_resume(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    text = extract_text_from_pdf(file_path)

    profile = extract_profile(text)
    profile = adjust_for_role(profile, "SDE")

    score = predict_score(profile)
    score = apply_boost(profile, score)

    interviews = get_interviews(profile)
    explanation = generate_explanation(profile, score, interviews, role="SDE")

    level = get_level(score)
    companies = suggest_companies(score)
    weaknesses = get_weaknesses(profile)

    confidence = get_confidence(profile)
    user_type = classify_user(profile)
    gaps = skill_gap(profile)
    plan = roadmap(profile)

    return {
        "profile": profile,
        "score": score,
        "level": level,
        "profile_type": user_type,
        "confidence": confidence,
        "skill_gaps": gaps,
        "roadmap": plan,
        "recommended_companies": companies,
        "weaknesses": weaknesses,
        "interviews": interviews,
        "analysis": explanation
    }


# =====================================================
# 💥 WHAT-IF SIMULATOR (UPGRADED)
# =====================================================

@app.post("/simulate")
def simulate(data: dict):
    def safe_get(obj, key, default=None):
        try:
            return obj.get(key, default)
        except Exception:
            try:
                return obj[key]
            except Exception:
                return default

    text = safe_get(data, "text")
    changes = safe_get(data, "changes", {}) or {}
    incoming_profile = safe_get(data, "profile")

    if text:
        profile = extract_profile(text)
    elif isinstance(incoming_profile, dict):
        # Allow simulation from already-extracted profile (e.g. PDF upload flow)
        profile = incoming_profile.copy()
    else:
        return {
            "error": "Provide either 'text' or 'profile' for simulation.",
            "current_score": 0,
            "improved_score": 0,
            "impact": 0,
            "priority_changes": [],
            "message": "Simulation could not run due to missing input."
        }

    original_profile = profile.copy()

    # Apply changes
    for key, value in changes.items():
        if key in profile:
            profile[key] = value

    original_score = apply_boost(original_profile, predict_score(original_profile))
    new_score = apply_boost(profile, predict_score(profile))

    impact = round(new_score - original_score, 2)

    # 🔥 SMART MESSAGE ENGINE
    if impact > 40:
        insight = "🚀 Massive improvement potential! You're close to top-tier companies."
    elif impact > 20:
        insight = "📈 Strong improvement possible with focused effort."
    else:
        insight = "⚡ Small improvements can still boost your chances."

    return {
        "current_score": original_score,
        "improved_score": new_score,
        "impact": impact,
        "priority_changes": sorted(changes.keys()),
        "message": f"{insight} (+{impact} points)"
    }