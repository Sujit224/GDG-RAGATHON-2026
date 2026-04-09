"""
Ingestion Pipeline for Lucknow Foodie Guide
=============================================
Loads restaurant data from JSON, creates rich text documents,
embeds them using sentence-transformers, and saves embeddings to disk.

Usage:
    python -m src.ingest
    # or
    python src/ingest.py
"""

import json
import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "restaurants.json")
EMBEDDINGS_DIR = os.path.join(BASE_DIR, "src", "embeddings")
EMBEDDINGS_PATH = os.path.join(EMBEDDINGS_DIR, "restaurant_embeddings.pkl")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # fast, lightweight, runs locally


def build_document(restaurant: dict) -> str:
    """
    Convert a restaurant dict into a rich text document
    optimised for semantic search. Combines all fields into
    a natural-language paragraph that captures maximum context.
    """
    name = restaurant["name"]
    area = restaurant["area"]
    address = restaurant["address"]
    cuisines = ", ".join(restaurant["cuisine"])
    price = restaurant["price_range"]
    cost = restaurant.get("cost_for_two", "N/A")
    veg = restaurant["veg_nonveg"]
    dishes = ", ".join(restaurant["signature_dishes"])
    hours = restaurant["opening_hours"]
    vibes = ", ".join(restaurant["vibe"])
    rating = restaurant["rating"]
    desc = restaurant["description"]
    reviews = restaurant["reviews_summary"]
    distance = restaurant["distance_from_iiit_km"]

    doc = (
        f"{name} is a restaurant located in {area}, Lucknow at {address}. "
        f"It serves {cuisines} cuisine and is categorized as {veg}. "
        f"Price range: {price} (approx ₹{cost} for two). "
        f"Signature dishes include {dishes}. "
        f"Opening hours: {hours}. "
        f"The vibe is described as: {vibes}. "
        f"Rating: {rating}/5. "
        f"Distance from IIIT Lucknow: {distance} km. "
        f"Description: {desc} "
        f"Customer reviews: {reviews}"
    )
    return doc


def ingest():
    """Main ingestion pipeline."""
    # ── Load dataset ─────────────────────────────────────────────
    print(f"📂 Loading dataset from {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        restaurants = json.load(f)
    print(f"   Found {len(restaurants)} restaurants")

    # ── Build documents ──────────────────────────────────────────
    documents = []
    metadatas = []

    for r in restaurants:
        documents.append(build_document(r))
        metadatas.append({
            "name": r["name"],
            "area": r["area"],
            "cuisine": ", ".join(r["cuisine"]),
            "price_range": r["price_range"],
            "cost_for_two": r.get("cost_for_two", 0),
            "veg_nonveg": r["veg_nonveg"],
            "signature_dishes": ", ".join(r["signature_dishes"]),
            "opening_hours": r["opening_hours"],
            "vibe": ", ".join(r["vibe"]),
            "rating": r["rating"],
            "distance_from_iiit_km": r["distance_from_iiit_km"],
            "maps_link": r.get("maps_link", ""),
        })

    # ── Compute embeddings ───────────────────────────────────────
    print(f"🧠 Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)

    print(f"📥 Embedding {len(documents)} documents ...")
    embeddings = model.encode(documents, show_progress_bar=True, normalize_embeddings=True)

    # ── Save to disk ─────────────────────────────────────────────
    os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

    data = {
        "embeddings": embeddings,  # numpy array (N, dim)
        "documents": documents,
        "metadatas": metadatas,
        "model_name": EMBEDDING_MODEL,
    }

    with open(EMBEDDINGS_PATH, "wb") as f:
        pickle.dump(data, f)

    print(f"✅ Ingestion complete! Saved {len(documents)} embeddings to {EMBEDDINGS_PATH}")
    return data


if __name__ == "__main__":
    ingest()
