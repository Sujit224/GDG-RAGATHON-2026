import pandas as pd

def load_data(path):
    try:
        df = pd.read_csv(path)
        df.fillna("", inplace=True)
        print(" Dataset loaded successfully")
        return df
    except Exception as e:
        print(" Error loading dataset:", e)
        return None