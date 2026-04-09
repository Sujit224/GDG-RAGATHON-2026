from __future__ import annotations

from pathlib import Path
import json
from typing import Any
from uuid import uuid4

from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Condition, Distance, FieldCondition, Filter, MatchValue, PointStruct, VectorParams

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_DIR / "dataset" / "restaurants.json"
QDRANT_PATH = BASE_DIR / "qdrant_data"
COLLECTION_NAME = "lucknow_foodie_hybrid"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_SIZE = 384


class LucknowFoodieHybridSearch:
    def __init__(self) -> None:
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)
        self.client = QdrantClient(path=str(QDRANT_PATH))
        self._ensure_collection()
        self._index_dataset()

    def _ensure_collection(self) -> None:
        collections = self.client.get_collections().collections
        names = {collection.name for collection in collections}
        if COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )

    def _load_dataset(self) -> list[dict[str, Any]]:
        if not DATASET_PATH.exists():
            raise FileNotFoundError(f"Dataset file not found: {DATASET_PATH}")
        with DATASET_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
        if not isinstance(data, list):
            raise ValueError("Dataset must be a JSON array of restaurants.")
        return data

    def _build_dense_text(self, restaurant: dict[str, Any]) -> str:
        dishes = ", ".join(restaurant.get("signature_dishes", []))
        reviews = " ".join(restaurant.get("reviews", []))
        return (
            f"Name: {restaurant.get('name', '')}. "
            f"Vibe: {restaurant.get('vibe', '')}. "
            f"Dishes: {dishes}. "
            f"Reviews: {reviews}"
        )

    def _index_dataset(self) -> None:
        if self.client.count(collection_name=COLLECTION_NAME, exact=True).count > 0:
            return

        restaurants = self._load_dataset()
        points: list[PointStruct] = []
        for restaurant in restaurants:
            dense_text = self._build_dense_text(restaurant)
            vector = self.embedder.encode(dense_text).tolist()
            payload = {
                "name": restaurant.get("name"),
                "vibe": restaurant.get("vibe"),
                "budget": restaurant.get("budget"),
                "is_veg": restaurant.get("is_veg"),
                "signature_dishes": restaurant.get("signature_dishes", []),
                "reviews": restaurant.get("reviews", []),
            }
            points.append(
                PointStruct(
                    id=str(uuid4()),
                    vector=vector,
                    payload=payload,
                )
            )

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)

    def _build_metadata_filter(
        self,
        budget: str | None = None,
        is_veg: bool | None = None,
    ) -> Filter | None:
        # Changed to strictly expect 'Condition' to satisfy the Python linter
        conditions: list[Condition] = []
        
        if budget is not None:
            conditions.append(
                FieldCondition(
                    key="budget",
                    match=MatchValue(value=budget),
                )
            )
        if is_veg is not None:
            conditions.append(
                FieldCondition(
                    key="is_veg",
                    match=MatchValue(value=is_veg),
                )
            )

        if not conditions:
            return None
        return Filter(must=conditions)

    def hybrid_search(
        self,
        query: str,
        budget: str | None = None,
        is_veg: bool | None = None,
        limit: int = 3,
    ) -> list[dict[str, Any]]:
        query_vector = self.embedder.encode(query).tolist()
        metadata_filter = self._build_metadata_filter(budget=budget, is_veg=is_veg)

        # Using the modern query_points API to avoid the search/search3 error
        response = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=metadata_filter,
            limit=limit,
            with_payload=True,
        )
        
        hits = response.points

        results: list[dict[str, Any]] = []
        for hit in hits:
            payload = hit.payload or {}
            results.append(
                {
                    "score": float(hit.score),
                    "name": payload.get("name"),
                    "vibe": payload.get("vibe"),
                    "budget": payload.get("budget"),
                    "is_veg": payload.get("is_veg"),
                    "signature_dishes": payload.get("signature_dishes", []),
                    "reviews": payload.get("reviews", []),
                }
            )
        return results


def suggest_places(
    query: str,
    budget: str | None = None,
    is_veg: bool | None = None,
    limit: int = 3,
) -> list[dict[str, Any]]:
    engine = LucknowFoodieHybridSearch()
    return engine.hybrid_search(query=query, budget=budget, is_veg=is_veg, limit=limit)


if __name__ == "__main__":
    sample_query = "Suggest a budget-friendly Biryani place with local vibe"
    matches = suggest_places(query=sample_query, budget="budget", is_veg=False, limit=3)
    print("Hybrid search results:")
    print(json.dumps(matches, indent=2, ensure_ascii=False))