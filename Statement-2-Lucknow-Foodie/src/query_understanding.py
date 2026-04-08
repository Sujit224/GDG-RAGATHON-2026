def parse_query(query):
    query = query.lower()

    filters = {
        "location": None,
        "max_price": None,
        "min_rating": None,
        "veg": None
    }

    # Budget
    if "cheap" in query or "budget" in query:
        filters["max_price"] = 400

    if "expensive" in query or "premium" in query:
        filters["max_price"] = 2000

    # Rating
    if "best" in query or "good" in query:
        filters["min_rating"] = 4.0

    # Veg filter
    if "veg" in query:
        filters["veg"] = "Veg"

    if "non veg" in query or "non-veg" in query:
        filters["veg"] = "Non-Veg"

    # Location detection
    locations = ["gomti nagar", "chowk", "hazratganj", "indira nagar", "aliganj"]
    for loc in locations:
        if loc in query:
            filters["location"] = loc.title()

    return query, filters