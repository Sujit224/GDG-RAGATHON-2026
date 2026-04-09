#!/usr/bin/env python3
"""
train_and_evaluate.py
=====================
Standalone script that:
  1. Generates a realistic dataset (if not present)
  2. Trains and compares Linear, RandomForest, GradientBoosting
  3. Saves the best model
  4. Runs example predictions to validate realism
  5. Shows what-if analysis

Run from the `backend/` directory:
    python scripts/train_and_evaluate.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.ml_service import train_and_save_model, predict_score, _generate_dataset
import json

print("=" * 60)
print("  HYBRID PLACEMENT PREDICTOR — TRAINING PIPELINE")
print("=" * 60)

# Generate dataset if missing
from services.ml_service import DATA_PATH
if not os.path.exists(DATA_PATH):
    print("\n[Step 1] Generating realistic dataset...")
    _generate_dataset()
else:
    print(f"\n[Step 1] Dataset found at {DATA_PATH} ✓")

# Train (force=True to always retrain during evaluation)
print("\n[Step 2–6] Training & Evaluating models...")
train_and_save_model(force=True)

# ─── Example Predictions ────────────────────────────────────────
TEST_CASES = [
    {
        "label":         "🌱 Early Stage — Low CGPA, no internships",
        "cgpa":          5.2,
        "projects":      1,
        "internships":   0,
        "communication": 4.0,
        "open_source":   0,
        "tech_stack":    "HTML/CSS|WordPress",
    },
    {
        "label":         "📈 Average — Decent CGPA, 1 internship",
        "cgpa":          7.1,
        "projects":      2,
        "internships":   1,
        "communication": 6.5,
        "open_source":   0,
        "tech_stack":    "React|Node.js",
    },
    {
        "label":         "🎯 Almost There — Good overall profile",
        "cgpa":          8.2,
        "projects":      3,
        "internships":   1,
        "communication": 7.5,
        "open_source":   1,
        "tech_stack":    "Django+React|Python",
    },
    {
        "label":         "🏆 Placement Ready — Top performer",
        "cgpa":          9.4,
        "projects":      5,
        "internships":   3,
        "communication": 9.0,
        "open_source":   1,
        "tech_stack":    "MERN|AI/ML|DevOps",
    },
    {
        "label":         "⚡ High CGPA but zero practical experience",
        "cgpa":          9.1,
        "projects":      0,
        "internships":   0,
        "communication": 8.0,
        "open_source":   0,
        "tech_stack":    "",
    },
]

print("\n" + "=" * 60)
print("  EXAMPLE PREDICTIONS")
print("=" * 60)

for tc in TEST_CASES:
    label = tc.pop("label")
    result = predict_score(tc)
    print(f"\n{label}")
    print(f"  Input   : CGPA={tc['cgpa']}, Projects={tc['projects']}, Internships={tc['internships']}, Comm={tc['communication']}, OSS={tc['open_source']}")
    print(f"  Score   : {result['score']} / 100  [{result['tier']}]  (Confidence: {result['confidence']})")
    print(f"  ML={result['ml_score']}  Rules={result['rule_score']}")
    print(f"  Reasons :")
    for r in result["reasons"]:
        print(f"    {r}")
    wi = result["what_if"]
    print(f"  What-If : +1 internship → score becomes {wi['plus_1_internship']} (Δ {wi['score_gain_internship']:+.1f})")
    print(f"            +1 project   → score becomes {wi['plus_1_project']} (Δ {wi['score_gain_project']:+.1f})")
    tc["label"] = label  # restore

print("\n" + "=" * 60)
print("  FEATURE IMPORTANCE (from best model)")
print("=" * 60)
sample_result = predict_score(TEST_CASES[-2])  # almost there case
fi = sample_result["feature_importance"]
if fi:
    for feat, val in sorted(fi.items(), key=lambda x: -x[1]):
        bar = "█" * int(val * 50)
        print(f"  {feat:<22} {val:.4f}  {bar}")
else:
    print("  (Feature importance not available for linear model)")

print("\n✅ Training and evaluation complete.\n")
