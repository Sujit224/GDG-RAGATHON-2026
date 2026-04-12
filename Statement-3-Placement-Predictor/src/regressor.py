import pandas as pd
import numpy as np
import pickle

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


def create_features(df):
    df = df.copy()
    
    # Feature Engineering (IMPORTANT)
    if "cgpa" in df.columns and "projects" in df.columns:
        df["cgpa_project_score"] = df["cgpa"] * df["projects"]
    
    if "internships" in df.columns:
        df["internship_weight"] = df["internships"] * 2
    
    return df


def train_model(df, target_col="readiness_score"):
    df = create_features(df)
    
    X = df.drop(columns=[target_col])
    y = df[target_col]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("gbr", GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=4,
            random_state=42
        ))
    ])

    model.fit(X, y)

    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)

    return model


def load_model():
    with open("model.pkl", "rb") as f:
        return pickle.load(f)


def predict(model, input_df):
    input_df = create_features(input_df)
    return model.predict(input_df)[0]