"""
Train a Gradient Boosting Regression model on normalized placement data.
Predicts a Readiness Score (0-100) from 7 student profile features.

Usage:
    python train_model.py
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

# ── Paths ──────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "..", "data", "normalized_placement_data.csv")
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "readiness_model.pkl")
SCALER_PATH = os.path.join(MODEL_DIR, "scaler.pkl")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

FEATURE_COLS = [
    "Academic_Score",
    "DSA_Skill",
    "Project_Quality",
    "Experience_Score",
    "OpenSource_Value",
    "Soft_Skills",
    "Tech_Stack_Score",
]
TARGET_COL = "Readiness_Score"


def train():
    """Load data, train model, evaluate, and save artifacts."""

    # ── 1. Load ────────────────────────────────────────────────────────
    print("[1/5] Loading dataset...")
    df = pd.read_csv(DATA_PATH)
    print(f"      Loaded {len(df)} rows  |  Columns: {list(df.columns)}")

    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # ── 2. Scale ───────────────────────────────────────────────────────
    print("[2/5] Scaling features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # ── 3. Split ───────────────────────────────────────────────────────
    print("[3/5] Splitting into train/test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"      Train: {len(X_train)}  |  Test: {len(X_test)}")

    # ── 4. Train ───────────────────────────────────────────────────────
    print("[4/5] Training GradientBoostingRegressor...")
    model = GradientBoostingRegressor(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.08,
        subsample=0.9,
        min_samples_split=5,
        min_samples_leaf=3,
        random_state=42,
    )
    model.fit(X_train, y_train)

    # Cross validation
    cv_scores = cross_val_score(model, X_scaled, y, cv=5, scoring="r2")
    print(f"      5-Fold CV R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")

    # ── 5. Evaluate ────────────────────────────────────────────────────
    print("[5/5] Evaluating on test set...")
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    metrics = {
        "r2_score": round(r2, 4),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "cv_r2_mean": round(cv_scores.mean(), 4),
        "cv_r2_std": round(cv_scores.std(), 4),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "features": FEATURE_COLS,
    }

    print(f"\n{'='*50}")
    print(f"  R² Score  : {r2:.4f}")
    print(f"  MAE       : {mae:.4f}")
    print(f"  RMSE      : {rmse:.4f}")
    print(f"  CV R² (5) : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"{'='*50}")

    # Feature importances
    importances = model.feature_importances_
    print("\n  Feature Importances:")
    for feat, imp in sorted(zip(FEATURE_COLS, importances), key=lambda x: -x[1]):
        bar = "#" * int(imp * 50)
        print(f"    {feat:20s} : {imp:.4f}  {bar}")

    # ── Save ───────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"\n[OK] Model saved to {MODEL_PATH}")
    print(f"[OK] Scaler saved to {SCALER_PATH}")
    print(f"[OK] Metrics saved to {METRICS_PATH}")

    return metrics


if __name__ == "__main__":
    train()
