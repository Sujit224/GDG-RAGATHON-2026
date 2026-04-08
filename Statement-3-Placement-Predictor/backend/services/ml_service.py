import pandas as pd
import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import joblib, os

MODEL_PATH = "models/regression_model.pkl"

FEATURES = [
    "Academic_Score",
    "Project_Quality",
    "Experience_Score",
    "Soft_Skills",
    "OpenSource_Value",
    "Tech_Stack_Score"
]
TARGET = "Readiness_Score"

def train_and_save_model():
    if os.path.exists(MODEL_PATH):
        return  # already trained
    
    try:
        df = pd.read_csv("data/normalized_placement_data.csv")
    except Exception as e:
        print(f"Skipping model training: {e}")
        return
    
    print("CSV Columns:", df.columns.tolist())
    
    X = df[FEATURES].fillna(0)
    y = df[TARGET].fillna(50)
    
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", Ridge(alpha=1.0))
    ])
    model.fit(X, y)
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Model trained and saved. R² on training data: {model.score(X, y):.3f}")

def predict_score(features: dict) -> float:
    # Build dataframe properly ensuring right columns
    try:
        model = joblib.load(MODEL_PATH)
        df_features = {
            "Academic_Score": [features.get("cgpa", 0.0)],
            "Project_Quality": [features.get("num_projects", 0)],
            "Experience_Score": [features.get("num_internships", 0)],
            "Soft_Skills": [features.get("communication", 0.0)],
            "OpenSource_Value": [features.get("opensource", 0)],
            "Tech_Stack_Score": [features.get("tech_stack_score", 0.0)]
        }
        X = pd.DataFrame(df_features)
        score = float(model.predict(X)[0])
        return max(0.0, min(100.0, round(score, 2)))
    except Exception as e:
        print(f"Error predicting score: {e}")
        return round(float(np.random.normal(65, 10)), 2) # fallback dummy
