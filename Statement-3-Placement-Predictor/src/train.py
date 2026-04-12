from regressor import train_model
import pandas as pd

# Load your dataset
df = pd.read_csv("your_dataset.csv")

# Train and save model
train_model(df)

print("✅ Model trained and saved as model.pkl")