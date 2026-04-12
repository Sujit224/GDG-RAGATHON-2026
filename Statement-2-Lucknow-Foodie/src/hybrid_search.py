from keyword_search import keyword_search
from semantic_search import semantic_search

def apply_filters(df, filters):
    if filters.get("location"):
        loc = str(filters["location"]).lower()
        df = df[df["location"].astype(str).str.lower().str.contains(loc, na=False)]

    if filters.get("near_iiit"):
        # If dataset provides distance, prefer it. Otherwise fall back to location keywords.
        if "distance_from_iiit_km" in df.columns:
            radius = float(filters.get("near_radius_km") or 10.0)
            df = df[df["distance_from_iiit_km"].astype(float) <= radius]
        else:
            df = df[df["location"].astype(str).str.lower().str.contains("golf city|chak ganjaria|palassio|lulu", regex=True, na=False)]

    if filters.get("max_price"):
        df = df[df["price_for_two"] <= filters["max_price"]]

    if filters.get("min_rating"):
        df = df[df["rating"] >= filters["min_rating"]]

    if filters.get("veg"):
        # If user asks Veg, include "Veg" and "Both". If Non-Veg, include "Non-Veg" and "Both".
        wanted = filters["veg"]
        if wanted == "Veg":
            df = df[df["veg_nonveg"].isin(["Veg", "Both"])]
        elif wanted == "Non-Veg":
            df = df[df["veg_nonveg"].isin(["Non-Veg", "Both"])]

    if filters.get("vibe"):
        vibe = str(filters["vibe"]).lower()
        if "vibe" in df.columns:
            df = df[df["vibe"].astype(str).str.lower().str.contains(vibe, na=False)]

    if filters.get("dish"):
        dish = str(filters["dish"]).lower()
        cols = [c for c in ["signature_dish", "cuisine", "name"] if c in df.columns]
        if cols:
            mask = False
            for c in cols:
                mask = mask | df[c].astype(str).str.lower().str.contains(dish, na=False)
            df = df[mask]

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
    combined_filtered = apply_filters(combined, filters)

    # Soft fallback: dish filters are often over-specific
    if combined_filtered.empty and filters.get("dish"):
        relaxed = dict(filters)
        relaxed["dish"] = None
        combined_filtered = apply_filters(combined, relaxed)

    # Soft fallback: "near IIIT" is ambiguous; relax radius a bit if still empty
    if combined_filtered.empty and filters.get("near_iiit") and "distance_from_iiit_km" in combined.columns:
        relaxed = dict(filters)
        relaxed["dish"] = relaxed.get("dish")  # keep other filters
        temp = combined.copy()
        temp = temp[temp["distance_from_iiit_km"].astype(float) <= 15.0]
        combined_filtered = apply_filters(temp, relaxed)

    return combined_filtered.sort_values(by="final_score", ascending=False)