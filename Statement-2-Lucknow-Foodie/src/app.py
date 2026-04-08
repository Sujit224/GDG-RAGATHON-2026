import streamlit as st

from data_loader import load_data
from keyword_search import build_tfidf
from semantic_search import embed_text, model
from hybrid_search import hybrid_search
from query_understanding import parse_query

# Load data
df = load_data("dataset/restaurants.csv")

# Build search systems (cache for speed)
@st.cache_resource
def setup():
    tfidf_vec, tfidf_matrix = build_tfidf(df["combined"])
    emb_matrix = embed_text(df["combined"].tolist())
    return tfidf_vec, tfidf_matrix, emb_matrix

tfidf_vec, tfidf_matrix, emb_matrix = setup()

# UI
st.title("🍕 Lucknow Foodie — Smart Search")

query = st.text_input("What are you craving? (e.g., cheap biryani in gomti nagar)")

if query:
    # Step 1: Query understanding
    filters = parse_query(query)

    # Step 2: Hybrid search
    results = hybrid_search(query, tfidf_vec, tfidf_matrix, model, emb_matrix, df)

    # Step 3: Apply filters
    if filters["price"]:
        results = results[results["price"].str.lower() == filters["price"]]

    if filters["location"]:
        results = results[results["location"].str.lower().str.contains(filters["location"])]

    if filters["cuisine"]:
        results = results[results["cuisine"].str.lower().str.contains(filters["cuisine"])]

    # Step 4: Show results
    st.subheader("Top Results")

    for _, row in results.head(5).iterrows():
        st.markdown(f"### {row['name']}")
        st.write(f"🍽 Cuisine: {row['cuisine']}")
        st.write(f"📍 Location: {row['location']}")
        st.write(f"💰 Price: {row['price']}")
        st.write(f"⭐ Rating: {row['rating']}")

        # Explanation (BONUS 🔥)
        explanation = f"Matches your query because it offers {row['cuisine']} in {row['location']}"

        if filters["price"]:
            explanation += f" and fits your {filters['price']} budget"

        st.info(explanation)
        st.markdown("---")