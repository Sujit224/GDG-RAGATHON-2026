import pandas as pd

def load_data(path):
    df = pd.read_csv(path)

    # Fill missing values
    df = df.fillna("")

    # Create combined text for search
    df["combined"] = (
        df["name"] + " " +
        df["cuisine"] + " " +
        df["description"] + " " +
        df["location"]
    )

    return df