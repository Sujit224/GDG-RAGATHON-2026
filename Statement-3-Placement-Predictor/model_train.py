import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle

# YAHAN DHYAN DO: Maine path change karke 'data/...' kar diya hai
df = pd.read_csv('data/normalized_placement_data.csv')

X = df[['Academic_Score', 'DSA_Skill', 'Project_Quality', 'Experience_Score', 'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score']]
y = df['Readiness_Score']

model = LinearRegression()
model.fit(X, y)

with open('placement_model.pkl', 'wb') as f:
    pickle.dump(model, f)

print("✅ Model trained perfectly on CSV data!")