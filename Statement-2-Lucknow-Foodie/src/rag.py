"""
RAG Engine for Lucknow Foodie Guide
=====================================
Hybrid search (metadata filters + semantic vector search)
combined with Groq LLM for conversational responses.

Usage:
    from src.rag import FoodieRAG
    rag = FoodieRAG()
    response = rag.query("Suggest a budget biryani place near campus")
"""

import os
import json
import re
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DIR = os.path.join(BASE_DIR, "src", "chroma_db")
COLLECTION_NAME = "lucknow_restaurants"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# ---------------------------------------------------------------------------
# Filter Extraction — Pre-filters for hybrid search
# ---------------------------------------------------------------------------

# Keywords mapped to ChromaDB metadata filters
VEG_KEYWORDS = {"veg", "vegetarian", "pure veg", "paneer", "dal", "sabzi", "chaat"}
NONVEG_KEYWORDS = {"non-veg", "nonveg", "non veg", "chicken", "mutton", "kebab",
                   "biryani", "nihari", "fish", "prawns", "meat", "egg"}
BUDGET_KEYWORDS = {"budget", "cheap", "affordable", "pocket-friendly", "₹", "under 500",
                   "student", "pocket friendly", "sasta", "dhaba"}
PREMIUM_KEYWORDS = {"premium", "fine dining", "expensive", "luxury", "fancy",
                    "special occasion", "₹₹₹₹", "high end", "upscale"}
NEARBY_KEYWORDS = {"near campus", "near iiit", "nearby", "close", "walking distance",
                   "around campus", "near college", "closest"}


def extract_filters(query: str) -> dict:
    """
    Extract metadata filters from the user query for pre-filtering
    in ChromaDB before semantic search.
    Returns a dict of ChromaDB `where` conditions.
    """
    q = query.lower()
    filters = {}

    # Veg / Non-veg filter
    if any(kw in q for kw in VEG_KEYWORDS) and not any(kw in q for kw in NONVEG_KEYWORDS):
        filters["veg_nonveg"] = {"$in": ["Veg", "Both"]}
    elif any(kw in q for kw in NONVEG_KEYWORDS):
        filters["veg_nonveg"] = {"$in": ["Non-Veg", "Both"]}

    # Budget filter
    if any(kw in q for kw in BUDGET_KEYWORDS):
        filters["cost_for_two"] = {"$lte": 500}

    # Premium filter
    if any(kw in q for kw in PREMIUM_KEYWORDS):
        filters["cost_for_two"] = {"$gte": 1000}

    # Nearby filter (within 5 km of IIIT)
    if any(kw in q for kw in NEARBY_KEYWORDS):
        filters["distance_from_iiit_km"] = {"$lte": 5.0}

    # Build ChromaDB where clause
    if len(filters) == 0:
        return None
    elif len(filters) == 1:
        key = list(filters.keys())[0]
        return {key: filters[key]}
    else:
        # Multiple filters → use $and
        conditions = [{k: v} for k, v in filters.items()]
        return {"$and": conditions}


# ---------------------------------------------------------------------------
# RAG Class
# ---------------------------------------------------------------------------

class FoodieRAG:
    """
    Core RAG engine combining:
    1. Keyword-based metadata pre-filtering
    2. Semantic vector search via ChromaDB
    3. Groq LLM for response generation
    """

    def __init__(self):
        # ── ChromaDB ──────────────────────────────────────────────
        self.client = chromadb.PersistentClient(path=CHROMA_DIR)
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL
        )
        self.collection = self.client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=self.ef,
        )

        # ── Groq LLM ─────────────────────────────────────────────
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in your .env file."
            )
        self.groq_client = Groq(api_key=GROQ_API_KEY)

        # ── Conversation history ──────────────────────────────────
        self.history: list[dict] = []

    def search(self, query: str, n_results: int = 6) -> list[dict]:
        """
        Hybrid search: metadata filters + semantic similarity.
        Returns list of matched restaurant documents with metadata.
        """
        where_filter = extract_filters(query)

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter,
                include=["documents", "metadatas", "distances"],
            )
        except Exception:
            # If filtered query returns too few results, fallback without filters
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )

        # Parse results into clean list
        matches = []
        if results and results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                meta = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                matches.append({
                    "document": doc,
                    "metadata": meta,
                    "similarity_score": round(1 - distance, 3),  # cosine → similarity
                })
        return matches

    def build_context(self, matches: list[dict]) -> str:
        """Build context string from search results for the LLM."""
        if not matches:
            return "No restaurants found matching the query."

        context_parts = []
        for i, m in enumerate(matches, 1):
            meta = m["metadata"]
            context_parts.append(
                f"Restaurant {i}: {meta.get('name', 'Unknown')}\n"
                f"  Area: {meta.get('area', 'N/A')}\n"
                f"  Cuisine: {meta.get('cuisine', 'N/A')}\n"
                f"  Price: {meta.get('price_range', 'N/A')} (~₹{meta.get('cost_for_two', 'N/A')} for two)\n"
                f"  Veg/Non-Veg: {meta.get('veg_nonveg', 'N/A')}\n"
                f"  Signature Dishes: {meta.get('signature_dishes', 'N/A')}\n"
                f"  Hours: {meta.get('opening_hours', 'N/A')}\n"
                f"  Vibe: {meta.get('vibe', 'N/A')}\n"
                f"  Rating: {meta.get('rating', 'N/A')}/5\n"
                f"  Distance from IIIT: {meta.get('distance_from_iiit_km', 'N/A')} km\n"
                f"  Maps: {meta.get('maps_link', 'N/A')}\n"
                f"  Similarity: {m.get('similarity_score', 'N/A')}"
            )
        return "\n\n".join(context_parts)

    def query(self, user_message: str) -> str:
        """
        Full RAG pipeline:
        1. Search for relevant restaurants
        2. Build context
        3. Generate response via Groq
        """
        # ── Step 1: Retrieve ──────────────────────────────────────
        matches = self.search(user_message)
        context = self.build_context(matches)

        # ── Step 2: Build prompt ──────────────────────────────────
        system_prompt = """You are the **Lucknow Foodie Guide** 🍽️ — a friendly, knowledgeable food recommendation bot for students of IIIT Lucknow.

Your job is to recommend restaurants based on the user's query using ONLY the restaurant data provided in the context below. Do NOT make up restaurants or information.

Guidelines:
- Be warm, enthusiastic, and conversational — like a foodie friend, not a database
- Recommend 2-4 restaurants per query (unless the user asks for more or fewer)
- For each recommendation, include: name, what makes it special, signature dishes, price range, distance from IIIT, and a Google Maps link
- Use emojis naturally (🍕 🔥 ⭐ etc.) but don't overdo it
- If the user asks about vibes (date night, party, study cafe), prioritise the vibe tags
- If a restaurant is far (>10 km), mention it's "Worth the trip!" or "A Lucknow pilgrimage"
- If no restaurants match, suggest the closest alternatives and explain why
- Keep responses concise but informative — students are busy!
- When mentioning price, use both the ₹ symbols AND actual cost for two
- If user asks a non-food question, gently redirect to food recommendations

IMPORTANT: Base ALL recommendations strictly on the provided context data. Never invent restaurants."""

        # ── Step 3: Generate via Groq ─────────────────────────────
        messages = [
            {"role": "system", "content": system_prompt},
        ]

        # Add conversation history (last 6 turns for context)
        for msg in self.history[-6:]:
            messages.append(msg)

        # Add current turn with context
        messages.append({
            "role": "user",
            "content": f"User Query: {user_message}\n\n--- Restaurant Data (from vector search) ---\n{context}",
        })

        try:
            response = self.groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"⚠️ Oops, something went wrong with the LLM: {str(e)}. But here are the raw results:\n\n{context}"

        # ── Step 4: Update history ────────────────────────────────
        self.history.append({"role": "user", "content": user_message})
        self.history.append({"role": "assistant", "content": answer})

        return answer

    def get_all_restaurants(self) -> list[dict]:
        """Return all restaurants from the collection (for browsing)."""
        results = self.collection.get(include=["metadatas"])
        return results["metadatas"] if results else []

    def reset_history(self):
        """Clear conversation history."""
        self.history = []


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("🚀 Initialising Lucknow Foodie RAG ...")
    rag = FoodieRAG()
    print("✅ Ready! Type your food queries (type 'quit' to exit)\n")

    while True:
        query = input("You: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            print("👋 Bon appétit!")
            break
        if not query:
            continue
        response = rag.query(query)
        print(f"\n🍽️ Foodie Bot: {response}\n")
