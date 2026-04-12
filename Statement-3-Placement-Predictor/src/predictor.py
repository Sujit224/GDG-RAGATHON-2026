import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
import joblib
import os

class PlacementPredictor:
    def __init__(self, model_path="models/rf_predictor.pkl", data_path="data/normalized_placement_data.csv"):
        self.model_path = model_path
        self.data_path = data_path
        self.model = self._load_or_train_model()

    def _load_data(self):
        """Load the placement data from CSV."""
        if os.path.exists(self.data_path):
            df = pd.read_csv(self.data_path)
  
            df = df.rename(columns={
                'Academic_Score': 'cgpa',
                'Tech_Stack_Score': 'tech_stack_count',
                'Project_Quality': 'projects_count',
                'Experience_Score': 'internships_count',
                'Soft_Skills': 'communication_score',
                'OpenSource_Value': 'opensource'
            })
    
            df['opensource'] = (df['opensource'] > 1).astype(int)
            return df
        else:
            return self._generate_mock_data()

    def _generate_mock_data(self):
        """Creates synthetic senior placement data if none exists."""
        np.random.seed(42)
        data = {
            'cgpa': np.random.uniform(6.0, 10.0, 100),
            'tech_stack_count': np.random.randint(2, 10, 100),
            'projects_count': np.random.randint(0, 5, 100),
            'internships_count': np.random.randint(0, 3, 100),
            'communication_score': np.random.randint(5, 11, 100),
            'opensource': np.random.randint(0, 2, 100),
            'readiness_score': np.random.randint(40, 101, 100)
        }
        return pd.DataFrame(data)

    def _load_or_train_model(self):
        if os.path.exists(self.model_path):
            return joblib.load(self.model_path)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        df = self._load_data()
        
        feature_columns = ['cgpa', 'tech_stack_count', 'projects_count', 'internships_count', 'communication_score', 'opensource']
        X = df[feature_columns]
        
        # Check for readiness score column (case-insensitive)
        if 'readiness_score' in df.columns:
            y = df['readiness_score']
        elif 'Readiness_Score' in df.columns:
            y = df['Readiness_Score']
        else:
            # Use mock data as target
            y = np.random.randint(40, 101, len(df))
        
        model.fit(X, y)
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        joblib.dump(model, self.model_path)
        return model

    def predict(self, profile):
        """
        Predicts readiness score (0-100) based on profile.
        """
        features = np.array([[
            profile.cgpa,
            len(profile.tech_stack),
            profile.projects_count,
            profile.internships_count,
            profile.communication_score,
            1 if profile.opensource_experience else 0
        ]])
        
        prediction = self.model.predict(features)[0]
        return round(min(max(prediction, 0), 100), 2)