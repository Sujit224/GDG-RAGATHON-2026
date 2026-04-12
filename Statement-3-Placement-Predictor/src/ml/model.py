import pickle
from src.config import MODEL_PATH
from src.ml.preprocess import process_features

def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

model = load_model()

def predict_score(data):
    features = process_features(data)
    score = model.predict([features])[0]
    return max(0, min(100, score))