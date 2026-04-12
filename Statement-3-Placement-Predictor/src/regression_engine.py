import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import pickle
import os
try:
    from .models import StudentProfile
except ImportError:
    from models import StudentProfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "normalized_placement_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "data", "model.pkl")

class RegressionEngine:
    def __init__(self):
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, "rb") as f:
                self.model = pickle.load(f)
        else:
            self.train()

    def train(self):
        if not os.path.exists(DATA_PATH):
            print(f"⚠️ Data not found at {DATA_PATH}. Using dummy model.")
            return

        df = pd.read_csv(DATA_PATH)
        
        # Features mapping
        X = df[['Academic_Score', 'DSA_Skill', 'Project_Quality', 'Experience_Score',
                'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score']]
        y = df['Readiness_Score']

        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X, y)

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(self.model, f)
        print("✅ Regression model trained and saved.")

    def predict(self, profile: StudentProfile) -> float:
        if self.model is None:
            # Fallback heuristic if model training failed
            score = (profile.academic_score * 5) + (profile.dsa_skill * 2) + (profile.project_quality * 2)
            return min(100.0, score)

        features = [[
            profile.academic_score,
            profile.dsa_skill,
            profile.project_quality,
            profile.experience_score,
            profile.opensource_value,
            profile.soft_skills,
            profile.tech_stack_score
        ]]
        
        score = self.model.predict(features)[0]
        return float(round(score, 2))

regression_engine = RegressionEngine()
predict_score = regression_engine.predict
