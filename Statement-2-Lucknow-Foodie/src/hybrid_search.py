from keyword_search import keyword_search
from semantic_search import semantic_search

def apply_filters(df, filters):
    if filters["location"]:
        df = df[df["location"] == filters["location"]]

    if filters["max_price"]:
        df = df[df["price_for_two"] <= filters["max_price"]]

    if filters["min_rating"]:
        df = df[df["rating"] >= filters["min_rating"]]

    if filters["veg"]:
        df = df[df["veg_nonveg"] == filters["veg"]]

    return df


def hybrid_search(df, query, filters):
    # Run both searches
    kw_results = keyword_search(df, query)
    sem_results = semantic_search(df, query)

    combined = sem_results.copy()

    # Keyword score
    combined["keyword_score"] = combined["name"].isin(kw_results["name"]).astype(int)

    # Final score
    combined["final_score"] = (
        0.7 * combined["semantic_score"] +
        0.3 * combined["keyword_score"]
    )

    # APPLY FILTERS HERE
    combined = apply_filters(combined, filters)

    return combined.sort_values(by="final_score", ascending=False)