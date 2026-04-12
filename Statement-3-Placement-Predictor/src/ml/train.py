import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
from pathlib import Path

# Base directory (points to src/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load dataset
DATA_PATH = BASE_DIR.parent / "data" / "normalized_placement_data.csv"
df = pd.read_csv(DATA_PATH)

# Features & target
X = df.drop("Readiness_Score", axis=1)
y = df["Readiness_Score"]

# Train model
model = LinearRegression()
model.fit(X, y)

# Ensure models folder exists
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

# Save model
MODEL_PATH = MODEL_DIR / "regression.pkl"
with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

print(f"Model trained and saved at {MODEL_PATH}")