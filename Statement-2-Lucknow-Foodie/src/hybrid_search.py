import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def hybrid_search(query, tfidf_vec, tfidf_matrix, emb_model, emb_matrix, df, alpha=0.5):
    
    # Keyword score
    query_tfidf = tfidf_vec.transform([query])
    keyword_scores = cosine_similarity(query_tfidf, tfidf_matrix)[0]

    # Semantic score
    query_emb = emb_model.encode([query])
    semantic_scores = cosine_similarity(query_emb, emb_matrix)[0]

    # Combine
    final_scores = alpha * keyword_scores + (1 - alpha) * semantic_scores

    df = df.copy()
    df["score"] = final_scores

    return df.sort_values(by="score", ascending=False)