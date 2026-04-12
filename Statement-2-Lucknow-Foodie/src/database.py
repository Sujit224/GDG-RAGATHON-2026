import os
import pandas as pd
base_path = os.path.dirname(__file__)

csv_path = os.path.join(base_path, "..", "dataset", "resturants.csv")

df = pd.read_csv(csv_path)

from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

docs = []

for index, row in df.iterrows():
    searchable_text = f"""
    Restaurant Name: {row['Name']}
    Location: {row['Location']}
    Signature Dishes: {row['Signature_Dishes']}
    Vibe and Atmosphere: {row['Vibe']}
    Reviews: {row['Reviews']}
    """
    
    metadata = {
        "name": row['Name'],
        "budget": int(row['Budget']), # e.g., 300
        "is_veg": bool(row['Is_Veg']), # True or False
        "distance_km": float(row['Distance_from_IIIT'])
    }

    docs.append(Document(page_content=searchable_text, metadata=metadata))

print(f"Successfully loaded {len(docs)} restaurants into documents!")


embed_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

vectorstore = Chroma.from_documents(
    documents=docs,
    embedding=embed_model,
    persist_directory="Foodie_DB"
)

