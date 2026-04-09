from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer


BASE_DIR = Path(__file__).resolve().parents[1]
TRAINING_DATA_PATH = BASE_DIR / "data" / "placement_data.csv"

FEATURE_COLUMNS = [
    "cgpa",
    "num_tech_skills",
    "num_projects",
    "num_internships",
    "has_open_source",
]
TARGET_COLUMN = "readiness_score"


def _clip_to_100(dataframe: pd.DataFrame) -> pd.DataFrame:
    clipped = dataframe.copy()
    clipped["cgpa"] = clipped["cgpa"].clip(lower=0.0, upper=10.0)
    clipped["num_tech_skills"] = clipped["num_tech_skills"].clip(lower=0)
    clipped["num_projects"] = clipped["num_projects"].clip(lower=0)
    clipped["num_internships"] = clipped["num_internships"].clip(lower=0)
    clipped["has_open_source"] = clipped["has_open_source"].clip(lower=0, upper=1)
    return clipped


def build_regression_pipeline() -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "numeric_pass",
                FunctionTransformer(_clip_to_100, validate=False),
                FEATURE_COLUMNS,
            )
        ],
        remainder="drop",
        verbose_feature_names_out=False,
    )
    model = RandomForestRegressor(
        n_estimators=250,
        max_depth=10,
        min_samples_split=2,
        random_state=42,
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", model),
        ]
    )


def train_model(csv_path: str | Path = TRAINING_DATA_PATH) -> Pipeline:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Training CSV not found: {path}")

    dataframe = pd.read_csv(path)
    missing_cols = [col for col in FEATURE_COLUMNS + [TARGET_COLUMN] if col not in dataframe.columns]
    if missing_cols:
        raise ValueError(f"Training data missing columns: {missing_cols}")

    X_train = dataframe[FEATURE_COLUMNS]
    y_train = dataframe[TARGET_COLUMN]

    pipeline = build_regression_pipeline()
    pipeline.fit(X_train, y_train)
    return pipeline


def _feature_row_from_resume(resume_json: dict[str, Any]) -> pd.DataFrame:
    tech_stack = resume_json.get("tech_stack", []) or []
    projects = resume_json.get("projects", []) or []
    internships = resume_json.get("internships", []) or []
    open_source = resume_json.get("open_source_experience", []) or []

    row = {
        "cgpa": float(resume_json.get("cgpa") or 0.0),
        "num_tech_skills": int(len(tech_stack)),
        "num_projects": int(len(projects)),
        "num_internships": int(len(internships)),
        "has_open_source": 1 if len(open_source) > 0 else 0,
    }
    return pd.DataFrame([row], columns=FEATURE_COLUMNS)


def predict_readiness_score(resume_json: dict[str, Any], trained_pipeline: Pipeline | None = None) -> float:
    model = trained_pipeline if trained_pipeline is not None else train_model()
    input_row = _feature_row_from_resume(resume_json)
    prediction = float(model.predict(input_row)[0])
    return max(0.0, min(100.0, round(prediction, 2)))


if __name__ == "__main__":
    sample_resume_json = {
        "cgpa": 8.4,
        "tech_stack": ["python", "sql", "pytorch", "docker", "aws"],
        "projects": ["RAG chatbot", "placement analytics dashboard", "vision classifier"],
        "internships": ["SDE Intern at StartupX"],
        "open_source_experience": ["Contributed 15 PRs to open-source ML repositories"],
    }
    model = train_model()
    score = predict_readiness_score(sample_resume_json, trained_pipeline=model)
    print(f"Predicted Readiness Score: {score}")
