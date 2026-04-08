from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')

def semantic_search(df, query):
    # Combine text columns
    texts = (df['name'] + " " + df['cuisine'] + " " + df['location']).tolist()

    # Convert to embeddings
    embeddings = model.encode(texts)
    query_embedding = model.encode([query])

    # Compute similarity (dot product)
    scores = np.dot(embeddings, query_embedding.T).flatten()

    df = df.copy()
    df["semantic_score"] = scores

    return df.sort_values(by="semantic_score", ascending=False)