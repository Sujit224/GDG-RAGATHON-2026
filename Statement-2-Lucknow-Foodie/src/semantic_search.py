from sentence_transformers import SentenceTransformer

# Load once
model = SentenceTransformer('all-MiniLM-L6-v2')

def embed_text(texts):
    return model.encode(texts, show_progress_bar=True)