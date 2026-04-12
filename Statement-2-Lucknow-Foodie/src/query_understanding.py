import re


def _extract_rupee_cap(q: str):
    # Examples: "under 500", "<500", "below ₹600", "max 700"
    m = re.search(r"(under|below|max|<=|<)\s*₹?\s*(\d{2,5})", q)
    if m:
        return int(m.group(2))
    return None


def _extract_min_rating(q: str):
    # Examples: "rating above 4.2", ">=4", "4.5+"
    m = re.search(r"(above|over|>=)\s*(\d(?:\.\d)?)", q)
    if m:
        return float(m.group(2))
    m = re.search(r"(\d(?:\.\d)?)\s*\+", q)
    if m:
        return float(m.group(1))
    return None


def parse_query(query: str):
    q = query.lower().strip()

    filters = {
        "location": None,          # string (substring match)
        "near_iiit": False,        # bool (distance filter if available)
        "max_price": None,         # int
        "min_rating": None,        # float
        "veg": None,               # "Veg" | "Non-Veg" | None
        "vibe": None,              # string
        "dish": None,              # string
    }

    # Near campus intent
    if any(k in q for k in ["iiit lucknow", "near iiit", "near campus", "around iiit", "around campus", "close to iiit"]):
        filters["near_iiit"] = True

    # Budget
    rupee_cap = _extract_rupee_cap(q)
    if rupee_cap is not None:
        filters["max_price"] = rupee_cap
    elif "cheap" in q or "budget" in q or "student" in q or "affordable" in q:
        filters["max_price"] = 500
    elif "premium" in q or "fine dine" in q or "luxury" in q or "expensive" in q:
        filters["max_price"] = 2500

    # Rating
    min_rating = _extract_min_rating(q)
    if min_rating is not None:
        filters["min_rating"] = min_rating
    elif any(k in q for k in ["best", "top", "highly rated", "must try"]):
        filters["min_rating"] = 4.2

    # Veg / non-veg
    if "non veg" in q or "non-veg" in q:
        filters["veg"] = "Non-Veg"
    elif re.search(r"\bveg\b", q):
        filters["veg"] = "Veg"

    # Vibe detection (keep single best match)
    vibe_keywords = [
        "rooftop", "cafe", "street", "family", "date", "romantic", "quiet",
        "premium", "luxury", "brewery", "buffet", "late night", "breakfast"
    ]
    for vk in vibe_keywords:
        if vk in q:
            filters["vibe"] = vk
            break

    # Dish intent: keep it conservative to avoid over-filtering
    dish_keywords = [
        "biryani", "kebab", "kababs", "chaat", "basket chaat", "coffee", "pizza",
        "momos", "burger", "roll", "pasta", "dessert", "pastry", "kachori",
        "bun maska", "tandoori", "buffet", "bbq"
    ]
    for dk in sorted(dish_keywords, key=len, reverse=True):
        if dk in q:
            filters["dish"] = dk
            break

    # Location detection (substring match; include common student areas + malls)
    locations = [
        "chak ganjaria",
        "sushant golf city",
        "golf city",
        "gomti nagar",
        "gomti nagar extension",
        "hazratganj",
        "chowk",
        "indira nagar",
        "aliganj",
        "chinhat",
        "phoenix palassio",
        "lulu mall",
    ]
    for loc in locations:
        if loc in q:
            filters["location"] = loc
            break

    return q, filters