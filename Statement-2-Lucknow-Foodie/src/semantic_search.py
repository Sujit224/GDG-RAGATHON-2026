from sentence_transformers import SentenceTransformer
import numpy as np

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')
_CACHE = {"texts_hash": None, "embeddings": None}


def _hash_texts(texts):
    # Fast-ish stable hash for caching (avoid importing hashlib for speed/size)
    return (len(texts), sum(len(t) for t in texts))

def semantic_search(df, query):
    # Combine text columns
    base = (df['name'].astype(str) + " " + df['cuisine'].astype(str) + " " + df['location'].astype(str))
    if "signature_dish" in df.columns:
        base = base + " " + df["signature_dish"].astype(str)
    if "vibe" in df.columns:
        base = base + " " + df["vibe"].astype(str)
    texts = base.tolist()

    # Convert to embeddings
    h = _hash_texts(texts)
    if _CACHE["texts_hash"] != h:
        _CACHE["embeddings"] = model.encode(texts)
        _CACHE["texts_hash"] = h
    embeddings = _CACHE["embeddings"]
    query_embedding = model.encode([query])

    # Compute similarity (dot product)
    scores = np.dot(embeddings, query_embedding.T).flatten()

    df = df.copy()
    df["semantic_score"] = scores

    return df.sort_values(by="semantic_score", ascending=False)