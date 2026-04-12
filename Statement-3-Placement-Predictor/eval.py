import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "normalized_placement_data.csv")

if not os.path.exists(DATA_PATH):
    print("Cannot find dataset")
    exit(1)

df = pd.read_csv(DATA_PATH)
X = df[['Academic_Score', 'DSA_Skill', 'Project_Quality', 'Experience_Score',
        'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score']]
y = df['Readiness_Score']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.4f}")
print(f"R2: {r2:.4f}")
