def keyword_search(df, query):
    query = query.lower()

    results = df[
        df['name'].str.lower().str.contains(query) |
        df['cuisine'].str.lower().str.contains(query) |
        df['location'].str.lower().str.contains(query)
    ]

    results = results.copy()
    results["keyword_score"] = 1.0

    return results