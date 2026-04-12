"""
lucknow_foodie_data_utils.py
────────────────────────────
Utility functions to load, filter and prepare the restaurant dataset
for the FastAPI + RAG backend of the Lucknow Foodie Guide.

Usage:
    from lucknow_foodie_data_utils import RestaurantDB
    db = RestaurantDB("lucknow_restaurants.json")
    results = db.search(vibe="date-night", diet="veg", budget_max=700)
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


# ── Data class mirroring the JSON schema ──────────────────────────────────────

@dataclass
class Restaurant:
    id: str
    name: str
    area: str
    category: str
    vibe: list[str]
    budget_per_person_inr: int
    budget_label: str
    cuisine: list[str]
    type: str                   # "Veg" | "Non-Veg" | "Both"
    signature_dishes: list[str]
    rating: float
    distance_from_campus_km: float
    hours: dict
    phone: str
    address: str
    google_maps_url: str
    accepts_upi: bool
    home_delivery: bool
    dine_in: bool
    takeaway: bool
    popular_with_students: bool
    review_summary: str
    tags: list[str]
    latitude: float
    longitude: float

    # Computed helper: plain-text blob for RAG embedding
    def to_rag_text(self) -> str:
        """Returns a rich plain-text document to be embedded into a vector store."""
        dishes = ", ".join(self.signature_dishes)
        vibes  = ", ".join(self.vibe)
        tags   = ", ".join(self.tags)
        hours  = f"{self.hours.get('open','?')} – {self.hours.get('close','?')}, {self.hours.get('days','?')}"

        features = []
        if self.home_delivery:  features.append("home delivery available")
        if self.dine_in:        features.append("dine-in")
        if self.takeaway:       features.append("takeaway")
        if self.accepts_upi:    features.append("UPI accepted")
        if self.popular_with_students: features.append("popular with students")

        return (
            f"Restaurant: {self.name}\n"
            f"Location: {self.area}, Lucknow\n"
            f"Address: {self.address}\n"
            f"Category: {self.category}\n"
            f"Cuisine: {', '.join(self.cuisine)}\n"
            f"Diet type: {self.type}\n"
            f"Vibe: {vibes}\n"
            f"Budget: ₹{self.budget_per_person_inr} per person ({self.budget_label})\n"
            f"Rating: {self.rating}/5\n"
            f"Distance from IIIT Lucknow: {self.distance_from_campus_km} km\n"
            f"Hours: {hours}\n"
            f"Signature dishes: {dishes}\n"
            f"Tags: {tags}\n"
            f"Features: {', '.join(features)}\n"
            f"Review: {self.review_summary}\n"
        )


# ── Main DB class ──────────────────────────────────────────────────────────────

class RestaurantDB:
    """
    In-memory restaurant database built from the JSON dataset.
    Provides structured filters and RAG-ready text export.
    """

    def __init__(self, json_path: str = "lucknow_restaurants.json"):
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Dataset not found at: {json_path}")
        with open(json_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.restaurants: list[Restaurant] = [
            Restaurant(**r) for r in raw["restaurants"]
        ]
        self.meta = raw.get("metadata", {})
        print(f"[RestaurantDB] Loaded {len(self.restaurants)} restaurants.")

    # ── Core search / filter ──────────────────────────────────────────────────

    def search(
        self,
        query: Optional[str] = None,          # fuzzy text match on name/dish/review
        vibe: Optional[str] = None,            # e.g. "date-night", "study-cafe"
        diet: Optional[str] = None,            # "veg" | "non-veg" | "both"
        budget_max: Optional[int] = None,      # max ₹ per person
        budget_label: Optional[str] = None,    # "very-budget"|"budget"|"mid-range"|"expensive"
        cuisine: Optional[str] = None,         # e.g. "Awadhi", "Chinese"
        dish: Optional[str] = None,            # e.g. "biryani", "kebab"
        area: Optional[str] = None,            # e.g. "Gomti Nagar"
        delivery: Optional[bool] = None,       # True = only delivery-available
        max_distance_km: Optional[float] = None,
        top_n: int = 5,
        sort_by: str = "rating",              # "rating" | "distance" | "budget"
    ) -> list[Restaurant]:
        """
        Filter restaurants by multiple criteria and return top_n results.
        Designed to be called from the FastAPI /recommend endpoint.
        """
        results = self.restaurants[:]

        # ── Diet filter ──────────────────────────────────────────────────────
        if diet:
            diet_lower = diet.lower()
            if diet_lower == "veg":
                results = [r for r in results if r.type.lower() in ("veg", "both")]
            elif diet_lower == "non-veg":
                results = [r for r in results if r.type.lower() in ("non-veg", "both")]

        # ── Budget filters ────────────────────────────────────────────────────
        if budget_max is not None:
            results = [r for r in results if r.budget_per_person_inr <= budget_max]
        if budget_label:
            results = [r for r in results if r.budget_label == budget_label.lower()]

        # ── Vibe filter ───────────────────────────────────────────────────────
        if vibe:
            vibe_lower = vibe.lower().replace(" ", "-")
            results = [r for r in results if any(vibe_lower in v for v in r.vibe)]

        # ── Cuisine filter ────────────────────────────────────────────────────
        if cuisine:
            cuisine_lower = cuisine.lower()
            results = [
                r for r in results
                if any(cuisine_lower in c.lower() for c in r.cuisine)
            ]

        # ── Dish filter ───────────────────────────────────────────────────────
        if dish:
            dish_lower = dish.lower()
            results = [
                r for r in results
                if any(dish_lower in d.lower() for d in r.signature_dishes)
                or any(dish_lower in t for t in r.tags)
            ]

        # ── Area / location filter ────────────────────────────────────────────
        if area:
            area_lower = area.lower()
            results = [r for r in results if area_lower in r.area.lower()]

        # ── Delivery filter ───────────────────────────────────────────────────
        if delivery is not None:
            results = [r for r in results if r.home_delivery == delivery]

        # ── Distance filter ───────────────────────────────────────────────────
        if max_distance_km is not None:
            results = [r for r in results if r.distance_from_campus_km <= max_distance_km]

        # ── Text / query filter ───────────────────────────────────────────────
        if query:
            query_lower = query.lower()
            results = [
                r for r in results
                if (query_lower in r.name.lower()
                    or query_lower in r.review_summary.lower()
                    or any(query_lower in d.lower() for d in r.signature_dishes)
                    or any(query_lower in t for t in r.tags)
                    or any(query_lower in c.lower() for c in r.cuisine))
            ]

        # ── Sort ──────────────────────────────────────────────────────────────
        if sort_by == "distance":
            results.sort(key=lambda r: r.distance_from_campus_km)
        elif sort_by == "budget":
            results.sort(key=lambda r: r.budget_per_person_inr)
        else:  # default: rating
            results.sort(key=lambda r: r.rating, reverse=True)

        return results[:top_n]

    # ── RAG helpers ───────────────────────────────────────────────────────────

    def all_rag_documents(self) -> list[dict]:
        """
        Returns a list of dicts suitable for loading into a vector store
        (e.g. ChromaDB, FAISS, Pinecone).

        Each document has:
          - 'id'       : restaurant ID string
          - 'text'     : rich plain-text blob for embedding
          - 'metadata' : structured dict for metadata filtering
        """
        return [
            {
                "id": r.id,
                "text": r.to_rag_text(),
                "metadata": {
                    "name": r.name,
                    "area": r.area,
                    "budget_label": r.budget_label,
                    "budget_inr": r.budget_per_person_inr,
                    "type": r.type,
                    "rating": r.rating,
                    "distance_km": r.distance_from_campus_km,
                    "delivery": r.home_delivery,
                    "vibe": r.vibe,
                    "cuisine": r.cuisine,
                    "tags": r.tags,
                },
            }
            for r in self.restaurants
        ]

    def get_by_id(self, restaurant_id: str) -> Optional[Restaurant]:
        for r in self.restaurants:
            if r.id == restaurant_id:
                return r
        return None

    def stats(self) -> dict:
        """Quick summary stats — useful for the admin/debug endpoint."""
        return {
            "total": len(self.restaurants),
            "veg_only": sum(1 for r in self.restaurants if r.type == "Veg"),
            "non_veg": sum(1 for r in self.restaurants if r.type == "Non-Veg"),
            "both": sum(1 for r in self.restaurants if r.type == "Both"),
            "with_delivery": sum(1 for r in self.restaurants if r.home_delivery),
            "avg_rating": round(
                sum(r.rating for r in self.restaurants) / len(self.restaurants), 2
            ),
            "areas": list({r.area for r in self.restaurants}),
        }


# ── Quick demo ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db = RestaurantDB("lucknow_restaurants.json")

    print("\n── Stats ──────────────────────────────")
    import pprint; pprint.pprint(db.stats())

    print("\n── Budget biryani places ──────────────")
    for r in db.search(dish="biryani", budget_max=300):
        print(f"  {r.name} ({r.area}) — ₹{r.budget_per_person_inr} | ⭐{r.rating}")

    print("\n── Veg + under ₹200 ───────────────────")
    for r in db.search(diet="veg", budget_max=200):
        print(f"  {r.name} ({r.area}) — ₹{r.budget_per_person_inr}")

    print("\n── Closest to campus ──────────────────")
    for r in db.search(sort_by="distance", max_distance_km=5, top_n=3):
        print(f"  {r.name} — {r.distance_from_campus_km} km")

    print("\n── RAG doc sample (R001) ──────────────")
    print(db.get_by_id("R001").to_rag_text())
