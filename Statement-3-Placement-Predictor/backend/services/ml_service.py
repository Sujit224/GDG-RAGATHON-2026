"""
Hybrid Placement Readiness Predictor — ml_service.py
=========================================================
Architecture:
  1. Realistic dataset generation (if not found)
  2. Feature Engineering  → 10 engineered features
  3. Model Comparison     → Linear, RandomForest, GradientBoosting
  4. Hybrid Scoring       → ML (70%) + Rule-Based (30%)
  5. Calibration          → Hard caps / boosts enforced AFTER hybrid merge
  6. Explainability       → Per-prediction reasons + confidence band
  7. What-If Analysis     → score sensitivity to +1 internship / +1 project
"""

import os
import numpy as np
import pandas as pd
import joblib
from typing import List

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ──────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────
MODEL_PATH      = "models/hybrid_placement_model.pkl"
DATA_PATH       = "data/realistic_placement_data.csv"
FALLBACK_DATA   = "data/normalized_placement_data.csv"

STRONG_TECH = {"MERN", "AI/ML", "Django+React", "FastAPI", "Flutter",
               "DevOps", "Spring Boot", "Kubernetes", "Rust", "Go"}
MEDIUM_TECH = {"React", "Node.js", "Python", "Java", "SQL",
               "Firebase", "MongoDB", "TypeScript", "Vue.js"}


# ──────────────────────────────────────────────────────────────
# STEP 1 – DATASET GENERATION (called if realistic CSV missing)
# ──────────────────────────────────────────────────────────────
def _generate_dataset() -> pd.DataFrame:
    import random
    rng = np.random.default_rng(42)
    random.seed(42)

    TECH_POOL = {
        "strong": list(STRONG_TECH),
        "medium": list(MEDIUM_TECH),
        "weak":   ["HTML/CSS", "MS Office", "Basic Python", "WordPress"],
    }

    def sample_stack(tier):
        pool = TECH_POOL[tier]
        return "|".join(random.sample(pool, min(random.randint(1, 3), len(pool))))

    def make_profile(kind):
        if kind == "weak":
            cgpa    = round(float(rng.uniform(4.0, 6.5)), 2)
            proj    = int(rng.integers(0, 3))
            intern_ = int(rng.integers(0, 2))
            comm    = round(float(rng.uniform(2.0, 6.0)), 1)
            oss     = int(rng.choice([0, 1], p=[0.85, 0.15]))
            stack   = sample_stack(random.choice(["weak", "medium"]))
        elif kind == "medium":
            cgpa    = round(float(rng.uniform(6.5, 8.5)), 2)
            proj    = int(rng.integers(1, 5))
            intern_ = int(rng.integers(0, 3))
            comm    = round(float(rng.uniform(5.0, 8.0)), 1)
            oss     = int(rng.choice([0, 1], p=[0.55, 0.45]))
            stack   = sample_stack(random.choices(["weak","medium","strong"], [0.2,0.5,0.3])[0])
        else:
            cgpa    = round(float(rng.uniform(8.0, 10.0)), 2)
            proj    = int(rng.integers(3, 8))
            intern_ = int(rng.integers(1, 5))
            comm    = round(float(rng.uniform(7.0, 10.0)), 1)
            oss     = int(rng.choice([0, 1], p=[0.25, 0.75]))
            stack   = sample_stack(random.choices(["medium","strong"], [0.3,0.7])[0])
        return dict(cgpa=cgpa, projects=proj, internships=intern_,
                    communication=comm, open_source=oss, tech_stack=stack)

    def target(r):
        tech = r["tech_stack"].split("|")
        ts = sum(3 if t in STRONG_TECH else (1.5 if t in MEDIUM_TECH else 0.5) for t in tech)
        s  = (r["cgpa"]/10)*30 + (min(r["projects"],5)/5)*20
        s += (min(r["internships"],3)/3)*20 + (r["communication"]/10)*15
        s += r["open_source"]*5 + min(ts/9,1)*10
        if r["cgpa"] >= 9:   s += 8
        elif r["cgpa"] >= 8: s += 4
        if r["internships"] >= 2: s += 7
        elif r["internships"] == 0: s -= 5
        if r["projects"]  > 3:  s += 3
        elif r["projects"] <= 1: s -= 3
        if r["communication"] >= 8:  s += 3
        elif r["communication"] < 5: s -= 5
        if r["open_source"]: s += 4
        if r["cgpa"] < 6:    s = min(s, 60)
        if r["projects"] == 0: s = min(s, 55)
        return round(float(np.clip(s + rng.normal(0, 2.5), 5, 100)), 2)

    rows = (
        [make_profile("weak")   for _ in range(90)]  +
        [make_profile("medium") for _ in range(130)] +
        [make_profile("strong") for _ in range(80)]
    )
    df = pd.DataFrame(rows)
    df["readiness_score"] = df.apply(target, axis=1)
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)
    print(f"[DATA] Generated {len(df)}-row realistic dataset → {DATA_PATH}")
    return df


# ──────────────────────────────────────────────────────────────
# STEP 2 – FEATURE ENGINEERING
# ──────────────────────────────────────────────────────────────
def _tech_stack_score(stack_str: str) -> float:
    """Convert pipe-separated tech stack string into a 0–5 depth score."""
    if not stack_str or (isinstance(stack_str, float) and np.isnan(stack_str)):
        return 0.0
    tech = [t.strip() for t in str(stack_str).split("|")]
    raw = sum(3 if t in STRONG_TECH else (1.5 if t in MEDIUM_TECH else 0.5) for t in tech)
    return round(min(raw / 3.0, 5.0), 2)   # normalise to 0–5


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms raw columns into engineered features.
    Accepts both camelCase API inputs (via predict) and CSV column names.
    """
    out = pd.DataFrame()

    # Accept both naming conventions
    def _col(df, *names, default=0.0):
        for n in names:
            if n in df.columns:
                return df[n].astype(float)
        return pd.Series([default] * len(df), dtype=float)

    cgpa          = _col(df, "cgpa", "Academic_Score", default=7.0)
    projects      = _col(df, "projects", "Project_Quality", default=0.0)
    internships   = _col(df, "internships", "Experience_Score", default=0.0)
    communication = _col(df, "communication", "Soft_Skills", default=6.0)
    open_source   = _col(df, "open_source", "OpenSource_Value", default=0.0)

    # Tech stack
    if "tech_stack" in df.columns:
        tech_depth = df["tech_stack"].apply(_tech_stack_score)
    elif "Tech_Stack_Score" in df.columns:
        tech_depth = df["Tech_Stack_Score"].astype(float)
    else:
        tech_depth = pd.Series([0.0] * len(df), dtype=float)

    # --- Engineered features ---
    # 1  Academic score (normalised 0-10)
    out["academic_score"]     = cgpa.clip(0, 10)

    # 2  Project score: penalise 0, reward >3 slightly
    out["project_score"]      = projects.clip(0, 7).apply(
                                    lambda p: 0 if p == 0 else (p * 1.5 if p <= 3 else 4.5 + (p - 3) * 0.5))

    # 3  Internship weight (internships matter more than projects)
    out["internship_weight"]  = internships.clip(0, 4).apply(
                                    lambda i: 0 if i == 0 else (i * 2.5 if i <= 2 else 5 + (i-2) * 1.0))

    # 4  Tech depth (0–5)
    out["tech_depth"]         = tech_depth.clip(0, 5)

    # 5  Communication quality
    out["communication_score"]= communication.clip(0, 10)

    # 6  Open-source bonus
    out["opensource_bonus"]   = open_source.clip(0, 1) * 5

    # 7  Profile strength = cgpa × (1 + internship_ratio)
    out["profile_strength"]   = (cgpa / 10.0) * (1 + (internships.clip(0,3) / 3.0))

    # 8  Practical index: blend projects + internships + open_source
    out["practical_index"]    = (
        (projects.clip(0,6) / 6.0) * 0.4 +
        (internships.clip(0,4) / 4.0) * 0.4 +
        (open_source.clip(0,1)) * 0.2
    ) * 10  # scale to 0-10

    # 9  Soft impact: communication amplified by weak penalty
    out["soft_impact"]        = communication.clip(0, 10).apply(
                                    lambda c: c * 0.6 if c < 5 else c)

    return out.astype(float)   # ensure all numeric — fixes sklearn/pandas compat


FEATURE_NAMES = [
    "academic_score", "project_score", "internship_weight",
    "tech_depth", "communication_score", "opensource_bonus",
    "profile_strength", "practical_index", "soft_impact"
]


# ──────────────────────────────────────────────────────────────
# STEP 3 – DOMAIN RULE-BASED SCORE
# ──────────────────────────────────────────────────────────────
def _rule_based_score(cgpa, projects, internships, communication,
                      open_source, tech_stack_str):
    """Returns (rule_score: float, reasons: list[str])"""
    reasons = []
    score = 50.0   # neutral baseline

    # CGPA
    if cgpa >= 9.0:
        score += 20; reasons.append("🎓 High CGPA (≥9) gave a strong academic boost")
    elif cgpa >= 8.0:
        score += 10; reasons.append("📚 Good CGPA (8–9) provided a moderate academic boost")
    elif cgpa >= 7.0:
        score +=  4; reasons.append("📖 Decent CGPA (7–8) had a slight positive effect")
    elif cgpa < 6.0:
        score -= 15; reasons.append("⚠️ Low CGPA (below 6) significantly reduced the score")

    # Internships
    if internships >= 2:
        score += 20; reasons.append("💼 2+ internships strongly boosted industry readiness")
    elif internships == 1:
        score += 8;  reasons.append("💼 1 internship showed practical exposure")
    else:
        score -= 10; reasons.append("❌ No internships penalised industry readiness")

    # Projects
    if projects > 3:
        score += 10; reasons.append("🚀 Strong project portfolio (>3 projects) added points")
    elif projects >= 2:
        score +=  5; reasons.append("🛠️ Moderate project count (2–3) was helpful")
    elif projects == 1:
        score -=  2; reasons.append("🔧 Only 1 project — slightly weak portfolio")
    else:
        score -= 10; reasons.append("❌ No projects significantly hurt the profile")

    # Communication
    if communication > 7:
        score += 8;  reasons.append("🗣️ Strong communication skills gave a boost")
    elif communication >= 5:
        score += 2;  reasons.append("💬 Average communication had minimal impact")
    else:
        score -= 8;  reasons.append("⚠️ Poor communication skills penalised the score")

    # Open Source
    if open_source:
        score += 8;  reasons.append("🌐 Open-source contribution added a bonus")

    # Tech Stack
    tech = [t.strip() for t in tech_stack_str.split("|") if t.strip()]
    strong_count = sum(1 for t in tech if t in STRONG_TECH)
    if strong_count >= 2:
        score += 10; reasons.append("⚡ Strong tech stack (AI/ML, MERN, etc.) boosted score")
    elif strong_count == 1:
        score +=  5; reasons.append("🔬 At least one in-demand technology helped")
    elif not tech:
        score -=  5; reasons.append("⚠️ No recognisable tech stack detected")

    return float(np.clip(score, 5, 100)), reasons


# ──────────────────────────────────────────────────────────────
# STEP 4 + 5 – MODEL SELECTION & TRAINING
# ──────────────────────────────────────────────────────────────
def train_and_save_model(force: bool = False):
    if os.path.exists(MODEL_PATH) and not force:
        print("[ML] Model already exists. Skipping training.")
        return

    # Load or generate data
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
        target_col = "readiness_score"
    elif os.path.exists(FALLBACK_DATA):
        df = pd.read_csv(FALLBACK_DATA)
        target_col = "Readiness_Score"
    else:
        df = _generate_dataset()
        target_col = "readiness_score"

    # Feature engineering
    X = engineer_features(df)[FEATURE_NAMES].fillna(0)
    y = df[target_col].astype(float).clip(0, 100)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # ── Compare models ──
    candidates = {
        "Ridge":            Pipeline([("sc", StandardScaler()), ("m", Ridge(alpha=1.0))]),
        "RandomForest":     Pipeline([("sc", StandardScaler()),
                                       ("m", RandomForestRegressor(
                                           n_estimators=200, max_depth=8,
                                           min_samples_leaf=3, random_state=42))]),
        "GradientBoosting": Pipeline([("sc", StandardScaler()),
                                       ("m", GradientBoostingRegressor(
                                           n_estimators=200, max_depth=4,
                                           learning_rate=0.08, subsample=0.9,
                                           random_state=42))]),
    }

    print("\n─── Model Comparison (5-fold CV on train set) ───")
    best_name, best_model, best_r2 = None, None, -np.inf
    for name, pipe in candidates.items():
        cv = cross_val_score(pipe, X_train, y_train, cv=5, scoring="r2")
        print(f"  {name:<20} CV R²: {np.mean(cv):.4f} ± {np.std(cv):.4f}")
        if np.mean(cv) > best_r2:
            best_r2, best_name, best_model = np.mean(cv), name, pipe

    print(f"\n[ML] Selected: {best_name} (CV R² = {best_r2:.4f})")

    # ── Final training ──
    best_model.fit(X_train, y_train)

    # ── Evaluation ──
    y_pred = best_model.predict(X_test)
    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)
    print(f"\n─── Test Set Metrics ({best_name}) ───")
    print(f"  MAE  : {mae:.2f}")
    print(f"  RMSE : {rmse:.2f}")
    print(f"  R²   : {r2:.4f}\n")

    # Feature importance (if RF/GB)
    regressor = best_model.named_steps["m"]
    if hasattr(regressor, "feature_importances_"):
        fi = dict(zip(FEATURE_NAMES, regressor.feature_importances_))
        print("─── Feature Importances ───")
        for f, v in sorted(fi.items(), key=lambda x: -x[1]):
            print(f"  {f:<22} {v:.4f}")

    os.makedirs("models", exist_ok=True)
    joblib.dump(best_model, MODEL_PATH)
    print(f"\n[ML] Model saved → {MODEL_PATH}")


# ──────────────────────────────────────────────────────────────
# INTERNAL: core hybrid computation (no what-if recursion)
# ──────────────────────────────────────────────────────────────
def _load_model():
    if not os.path.exists(MODEL_PATH):
        train_and_save_model(force=True)
    return joblib.load(MODEL_PATH)


def _compute_score(cgpa, projects, internships, communication,
                   open_source, tech_stack_str, model):
    """
    Pure computation: no what-if, no recursion.
    Returns (final_score, ml_score, rule_score, tier, reasons, confidence)
    """
    # ── Build feature DataFrame ──
    row = pd.DataFrame([{
        "cgpa": cgpa, "projects": projects, "internships": internships,
        "communication": communication, "open_source": open_source,
        "tech_stack": tech_stack_str
    }])
    X = engineer_features(row)[FEATURE_NAMES].fillna(0)

    # ── ML Score ──
    ml_score = float(np.clip(model.predict(X)[0], 0, 100))

    # ── Rule-Based Score ──
    rule_score, reasons = _rule_based_score(
        cgpa, projects, internships, communication, open_source, tech_stack_str)

    # ── HYBRID: 70% ML + 30% Rule ──
    hybrid = (ml_score * 0.70) + (rule_score * 0.30)

    # ── Calibration / Post-processing ──
    if cgpa >= 9.0:
        hybrid = min(hybrid + 5, 100)
    elif cgpa >= 8.0:
        hybrid = min(hybrid + 2, 100)
    if internships >= 2:
        hybrid = min(hybrid + 5, 100)

    # Hard caps (applied last)
    if cgpa < 6.0:
        hybrid = min(hybrid, 60.0)
        reasons.append("🚧 Hard cap at 60: CGPA below 6.0")
    if projects == 0:
        hybrid = min(hybrid, 55.0)
        reasons.append("🚧 Hard cap at 55: zero projects on profile")
    if internships == 0 and cgpa < 7.0:
        hybrid = min(hybrid, 50.0)
        reasons.append("🚧 Hard cap at 50: no internships + low CGPA combination")

    final_score = round(float(np.clip(hybrid, 0, 100)), 2)

    # ── Tier labels ──
    if final_score >= 80:
        tier = "Placement Ready 🏆"
    elif final_score >= 65:
        tier = "Almost There 🎯"
    elif final_score >= 50:
        tier = "Needs Improvement 📈"
    elif final_score >= 35:
        tier = "Work In Progress 🔧"
    else:
        tier = "Early Stage 🌱"

    # ── Confidence band ──
    spread = abs(ml_score - rule_score)
    confidence = "High" if spread < 10 else ("Medium" if spread < 20 else "Low")

    return final_score, ml_score, rule_score, tier, reasons, confidence, X


# ──────────────────────────────────────────────────────────────
# STEP 6 + 7 – HYBRID PREDICT (public API)
# ──────────────────────────────────────────────────────────────
def predict_score(features: dict) -> dict:
    """
    Main prediction function.

    Input dict keys:
        cgpa, projects (or num_projects), internships (or num_internships),
        communication, open_source (or opensource), tech_stack (str/list)

    Returns:
        score          – final 0-100 float
        ml_score       – raw ML output
        rule_score     – pure rule-based score
        tier           – label (Placement Ready / Almost There / ...)
        reasons        – list of human-readable explanation strings
        confidence     – "High" / "Medium" / "Low"
        what_if        – dict with +1 internship and +1 project scenario scores
        feature_inputs – the normalised feature vector sent to ML
        feature_importance – dict mapping feature name to importance score
    """
    model = _load_model()

    # ── Normalise input keys ──
    cgpa          = float(features.get("cgpa", 0))
    projects      = int(features.get("projects", features.get("num_projects", 0)))
    internships   = int(features.get("internships", features.get("num_internships", 0)))
    communication = float(features.get("communication", 0))
    open_source   = int(features.get("open_source", features.get("opensource", 0)))

    # Tech stack – accept list or pipe-separated string
    raw_stack = features.get("tech_stack", "")
    if isinstance(raw_stack, list):
        tech_stack_str = "|".join(raw_stack)
    else:
        tech_stack_str = str(raw_stack)

    # Fallback: if no stack name but caller passes tech_stack_score
    if not tech_stack_str.strip() and "tech_stack_score" in features:
        tss = float(features["tech_stack_score"])
        tech_stack_str = "MERN" if tss >= 3 else ("React" if tss >= 1.5 else "")

    # ── Core computation ──
    final_score, ml_score, rule_score, tier, reasons, confidence, X = _compute_score(
        cgpa, projects, internships, communication,
        open_source, tech_stack_str, model
    )

    # ── What-If Analysis (no recursion — direct recompute) ──
    wi_intern_score, *_ = _compute_score(
        cgpa, projects, internships + 1, communication,
        open_source, tech_stack_str, model)
    wi_proj_score, *_ = _compute_score(
        cgpa, projects + 1, internships, communication,
        open_source, tech_stack_str, model)

    what_if = {
        "plus_1_internship":      round(float(wi_intern_score), 2),
        "plus_1_project":         round(float(wi_proj_score), 2),
        "score_gain_internship":  round(float(wi_intern_score) - final_score, 2),
        "score_gain_project":     round(float(wi_proj_score) - final_score, 2),
    }

    # ── Feature importance (from stored model, RF/GB only) ──
    regressor = model.named_steps.get("m") or model.named_steps.get("regressor")
    feature_importance = {}
    if hasattr(regressor, "feature_importances_"):
        feature_importance = {
            k: round(float(v), 4)
            for k, v in zip(FEATURE_NAMES, regressor.feature_importances_)
        }

    return {
        "score":              final_score,
        "ml_score":           round(float(ml_score), 2),
        "rule_score":         round(float(rule_score), 2),
        "tier":               tier,
        "reasons":            reasons,
        "confidence":         confidence,
        "what_if":            what_if,
        "feature_importance": feature_importance,
        "feature_inputs":     {k: round(float(v), 4) for k, v in X.iloc[0].items()},
    }
