import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_and_save_model():
    data_path = "data/normalized_placement_data.csv"
    model_dir = "models"
    model_path = os.path.join(model_dir, "regressor.pkl")

    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    print("Loading data...")
    df = pd.read_csv(data_path)

    features = [
        'Academic_Score', 'DSA_Skill', 'Project_Quality', 
        'Experience_Score', 'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score'
    ]
    target = 'Readiness_Score'

    X = df[features]
    y = df[target]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Training Random Forest Regressor...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    print(f"Model Evaluation Summary:")
    print(f"MSE: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")

    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

def predict_readiness(profile_dict):
    """
    Given a dictionary of features mapping to 1-10 scores, predict readiness.
    """
    model_path = "models/regressor.pkl"
    if not os.path.exists(model_path):
        train_and_save_model()
    
    model = joblib.load(model_path)
    features = [
        'Academic_Score', 'DSA_Skill', 'Project_Quality', 
        'Experience_Score', 'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score'
    ]
    # Ensure order
    input_data = pd.DataFrame([profile_dict], columns=features)
    prediction = model.predict(input_data)
    return prediction[0]

if __name__ == "__main__":
    train_and_save_model()
