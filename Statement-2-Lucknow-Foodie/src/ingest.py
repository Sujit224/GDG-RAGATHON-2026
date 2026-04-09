"""
Ingestion Pipeline for Lucknow Foodie Guide
=============================================
Loads restaurant data from JSON, creates rich text documents,
embeds them using sentence-transformers, and stores in ChromaDB.

Usage:
    python -m src.ingest
    # or
    python src/ingest.py
"""

import json
import os
import sys
import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "dataset", "restaurants.json")
CHROMA_DIR = os.path.join(BASE_DIR, "src", "chroma_db")
COLLECTION_NAME = "lucknow_restaurants"
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


def build_metadata(restaurant: dict) -> dict:
    """
    Extract structured metadata for ChromaDB filtering.
    ChromaDB metadata values must be str, int, float, or bool.
    """
    return {
        "name": restaurant["name"],
        "area": restaurant["area"],
        "cuisine": ", ".join(restaurant["cuisine"]),
        "price_range": restaurant["price_range"],
        "cost_for_two": restaurant.get("cost_for_two", 0),
        "veg_nonveg": restaurant["veg_nonveg"],
        "signature_dishes": ", ".join(restaurant["signature_dishes"]),
        "opening_hours": restaurant["opening_hours"],
        "vibe": ", ".join(restaurant["vibe"]),
        "rating": restaurant["rating"],
        "distance_from_iiit_km": restaurant["distance_from_iiit_km"],
        "maps_link": restaurant.get("maps_link", ""),
    }


def ingest():
    """Main ingestion pipeline."""
    # ── Load dataset ─────────────────────────────────────────────
    print(f"📂 Loading dataset from {DATASET_PATH}")
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        restaurants = json.load(f)
    print(f"   Found {len(restaurants)} restaurants")

    # ── Prepare documents ────────────────────────────────────────
    ids = []
    documents = []
    metadatas = []

    for r in restaurants:
        doc_id = f"restaurant_{r['id']}"
        ids.append(doc_id)
        documents.append(build_document(r))
        metadatas.append(build_metadata(r))

    # ── Setup ChromaDB ───────────────────────────────────────────
    print(f"🗄️  Initialising ChromaDB at {CHROMA_DIR}")
    client = chromadb.PersistentClient(path=CHROMA_DIR)

    # Use sentence-transformers for local embeddings (no API key needed)
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    # Delete existing collection if it exists (fresh ingest)
    try:
        client.delete_collection(name=COLLECTION_NAME)
        print("   Deleted existing collection (fresh start)")
    except ValueError:
        pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )

    # ── Upsert documents ─────────────────────────────────────────
    print(f"📥 Embedding and storing {len(documents)} documents ...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
    )

    print(f"✅ Ingestion complete! Collection '{COLLECTION_NAME}' has {collection.count()} documents.")
    return collection


if __name__ == "__main__":
    ingest()
