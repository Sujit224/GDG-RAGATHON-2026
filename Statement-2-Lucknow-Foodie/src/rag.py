"""
RAG Engine for Lucknow Foodie Guide
=====================================
Hybrid search (metadata filters + cosine similarity)
combined with Groq LLM for conversational responses.

Usage:
    from src.rag import FoodieRAG
    rag = FoodieRAG()
    response = rag.query("Suggest a budget biryani place near campus")
"""

import os
import pickle
import numpy as np
from scipy.spatial.distance import cosine
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from groq import Groq

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EMBEDDINGS_PATH = os.path.join(BASE_DIR, "src", "embeddings", "restaurant_embeddings.pkl")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# ---------------------------------------------------------------------------
# Filter Extraction — Pre-filters for hybrid search
# ---------------------------------------------------------------------------

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
    before semantic search.
    """
    q = query.lower()
    filters = {}

    if any(kw in q for kw in VEG_KEYWORDS) and not any(kw in q for kw in NONVEG_KEYWORDS):
        filters["veg"] = True
    elif any(kw in q for kw in NONVEG_KEYWORDS):
        filters["nonveg"] = True

    if any(kw in q for kw in BUDGET_KEYWORDS):
        filters["budget"] = True

    if any(kw in q for kw in PREMIUM_KEYWORDS):
        filters["premium"] = True

    if any(kw in q for kw in NEARBY_KEYWORDS):
        filters["nearby"] = True

    return filters


def apply_filters(metadatas: list[dict], filters: dict, diet_filters: list[str] = None) -> list[int]:
    """
    Return indices of restaurants that pass the filters.
    If no filters, return all indices.
    """
    if not filters:
        return list(range(len(metadatas)))

    valid = set(range(len(metadatas)))

    if filters.get("veg"):
        valid &= {i for i, m in enumerate(metadatas) if m["veg_nonveg"] in ("Veg", "Both")}
    if filters.get("nonveg"):
        valid &= {i for i, m in enumerate(metadatas) if m["veg_nonveg"] in ("Non-Veg", "Both")}
    if filters.get("budget"):
        valid &= {i for i, m in enumerate(metadatas) if m["cost_for_two"] <= 500}
    if filters.get("premium"):
        valid &= {i for i, m in enumerate(metadatas) if m["cost_for_two"] >= 1000}
    if filters.get("nearby"):
        valid &= {i for i, m in enumerate(metadatas) if m["distance_from_iiit_km"] <= 5.0}

    # Strict UI Dictionary Filters
    if diet_filters:
        strict_veg = any(d in diet_filters for d in ("Vegan", "Pure Veg", "Jain"))
        if strict_veg:
            valid &= {i for i, m in enumerate(metadatas) if m["veg_nonveg"] == "Veg" or m["veg_nonveg"] == "Both"}

    return list(valid)


# ---------------------------------------------------------------------------
# RAG Class
# ---------------------------------------------------------------------------

class FoodieRAG:
    """
    Core RAG engine combining:
    1. Keyword-based metadata pre-filtering
    2. Cosine similarity search via numpy
    3. Groq LLM for response generation
    """

    def __init__(self):
        # ── Load embeddings ───────────────────────────────────────
        if not os.path.exists(EMBEDDINGS_PATH):
            raise FileNotFoundError(
                f"Embeddings not found at {EMBEDDINGS_PATH}. Run ingestion first."
            )

        with open(EMBEDDINGS_PATH, "rb") as f:
            data = pickle.load(f)

        self.embeddings = data["embeddings"]      # numpy array (N, dim)
        self.documents = data["documents"]         # list of strings
        self.metadatas = data["metadatas"]          # list of dicts

        # ── Load embedding model for query encoding ───────────────
        self.model = SentenceTransformer(EMBEDDING_MODEL)

        # ── Groq LLM ─────────────────────────────────────────────
        if not GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY not found. Set it in your .env file."
            )
        self.groq_client = Groq(api_key=GROQ_API_KEY)

        # ── Conversation history ──────────────────────────────────
        self.history: list[dict] = []

    def search(self, query: str, diet_filters: list[str] = None, n_results: int = 6) -> list[dict]:
        """
        Hybrid search: metadata filters + cosine similarity.
        Returns list of matched restaurant documents with metadata.
        """
        # Step 1: Apply keyword filters & diet restrictions
        filters = extract_filters(query)
        valid_indices = apply_filters(self.metadatas, filters, diet_filters)

        # Step 2: Compute query embedding
        query_embedding = self.model.encode([query], normalize_embeddings=True)[0]

        # Step 3: Compute cosine similarities (only for filtered restaurants)
        similarities = []
        for idx in valid_indices:
            sim = 1 - cosine(query_embedding, self.embeddings[idx])
            similarities.append((idx, sim))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Take top n_results
        top_results = similarities[:n_results]

        # If filtered results are too few, fallback to all restaurants
        if len(top_results) < 3 and filters:
            all_sims = []
            for idx in range(len(self.metadatas)):
                sim = 1 - cosine(query_embedding, self.embeddings[idx])
                all_sims.append((idx, sim))
            all_sims.sort(key=lambda x: x[1], reverse=True)
            top_results = all_sims[:n_results]

        # Build results
        matches = []
        for idx, sim in top_results:
            matches.append({
                "document": self.documents[idx],
                "metadata": self.metadatas[idx],
                "similarity_score": round(sim, 3),
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

    def query(self, user_message: str, diet_filters: list[str] = None, allergies: str = "") -> str:
        """
        Full RAG pipeline:
        1. Search for relevant restaurants
        2. Build context
        3. Generate response via Groq
        """
        # ── Step 1: Retrieve ──────────────────────────────────────
        matches = self.search(user_message, diet_filters)
        context = self.build_context(matches)

        # ── Step 2: Build prompt ──────────────────────────────────
        system_prompt = """You are the **Lucknow Foodie Guide** 🍽️ — a highly advanced, premium food recommendation AI for IIIT Lucknow students.

Your job is to recommend restaurants based on the user's query using ONLY the data provided. Do NOT invent restaurants.

CRITICAL INSTRUCTION:
When you recommend a restaurant, you MUST format the recommendation as a specific structured tag so the UI can render a beautiful image card.
Do NOT just write text paragraphs about the restaurant. Use this exact literal syntax on a new line:
[CARD: Restaurant Name | Cuisine | Price Range | Rating | Distance from IIIT | Map Link]

Example of a correct response:
"Here is a great budget spot near campus!
[CARD: Sharma Ji Ka Dhaba | North Indian, Street Food | ₹ (Under 200) | 4.2 | 1.5 | https://g.co/kgs/xyz]
You should definitely try their signature Dal Makhani!"

Guidelines:
- Recommend 2-4 restaurants per query.
- Use emojis naturally but don't overdo it.
- If the user asks a non-food question, politely redirect to food.
- Make sure every component inside the [CARD: ...] is separated exactly by ' | '.
- NEVER miss a field inside the CARD tag. It must have exactly 6 sections separated by 5 pipes.
"""

        # ── Dynamically inject explicit dietary rules if provided ──
        if diet_filters or allergies:
            system_prompt += "\n\nCRITICAL DIETARY RESTRICTIONS FROM USER:\n"
            if diet_filters:
                system_prompt += f"- Required Tags: {', '.join(diet_filters)}\n"
            if allergies:
                system_prompt += f"- Custom Allergies/Aversions: {allergies}\n"
            system_prompt += "\nYou MUST strictly obey these restrictions. Verify the restaurant can safely accommodate them. If you cannot be sure, explicitly warn the user."

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
        """Return all restaurants (for browsing)."""
        return self.metadatas

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
