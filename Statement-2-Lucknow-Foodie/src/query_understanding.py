def parse_query(query):
    query = query.lower()

    filters = {
        "price": None,
        "location": None,
        "cuisine": None
    }

    # Price
    if "cheap" in query or "budget" in query or "low cost" in query:
        filters["price"] = "low"
    elif "expensive" in query or "luxury" in query:
        filters["price"] = "high"

    # Cuisine keywords
    cuisines = ["biryani", "pizza", "burger", "chinese", "north indian", "south indian"]
    for c in cuisines:
        if c in query:
            filters["cuisine"] = c

    # Location keywords (edit based on dataset)
    locations = ["gomti nagar", "hazratganj", "indira nagar", "aliganj"]
    for loc in locations:
        if loc in query:
            filters["location"] = loc

    return filters