import os
from typing import List, Dict, Any
from dotenv import load_dotenv

import chromadb
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from lucknow_foodie_data_utils import RestaurantDB

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.db = RestaurantDB("lucknow_restaurants.json")
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection_name = "lucknow_restaurants"
        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Initialize Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key and api_key != "your_gemini_api_key_here":
            genai.configure(api_key=api_key)
        
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print("[RAGEngine] Found existing ChromaDB collection.")
            if self.collection.count() == 0:
                self._embed_all()
        except:
            print("[RAGEngine] Creating new ChromaDB collection...")
            self.collection = self.chroma_client.create_collection(name=self.collection_name)
            self._embed_all()

        # Define system instruction for Gemini using system prompt directly might require passing it to generation config or as system_instruction
        self.system_prompt = (
            "You are 'Lucknow Foodie', a friendly and knowledgeable food guide bot "
            "specifically built for students of IIIT Lucknow. You know everything about "
            "Lucknow's food scene. Your job is to recommend restaurants from the provided context.\n"
            "Rules:\n"
            "- ONLY recommend restaurants from the provided context. Never make up "
            "restaurant names or details that are not in the context.\n"
            "- Always mention: restaurant name, area, approximate budget per person, "
            "distance from IIIT Lucknow, and 1-2 signature dishes.\n"
            "- If the student mentions a budget, only recommend places within that budget.\n"
            "- Be conversational, warm and use occasional Hinglish (e.g., 'yaar', "
            "'ekdum mast', 'must try kar') to feel relatable to students.\n"
            "- If asked about something outside food/restaurants, politely redirect.\n"
            "- End every recommendation with a practical tip (e.g., 'get there before "
            "8 PM or it sells out!' or 'Tuesday deals pe try karo!').\n"
        )
        
        if api_key and api_key != "your_gemini_api_key_here":
            self.model = genai.GenerativeModel(
                model_name='gemini-2.5-flash',
                system_instruction=self.system_prompt
            )

    def _embed_all(self):
        docs = self.db.all_rag_documents()
        texts = [d["text"] for d in docs]
        ids = [d["id"] for d in docs]
        metadatas = [d["metadata"] for d in docs]
        
        print(f"[RAGEngine] Embedding {len(docs)} documents. This may take a moment...")
        embeddings = self.embed_model.encode(texts).tolist()
        
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas
        )
        print("[RAGEngine] Embedding complete.")

    def parse_filters(self, query: str) -> Dict[str, Any]:
        """Extract structured filters from a natural language query."""
        ql = query.lower()
        filters = {}
        
        if "veg" in ql and "non-veg" not in ql:
            filters["diet"] = "veg"
        elif "non-veg" in ql or "chicken" in ql or "mutton" in ql:
            filters["diet"] = "non-veg"
            
        if "budget" in ql or "cheap" in ql or "under 300" in ql:
            filters["budget_max"] = 300
        elif "under 200" in ql:
            filters["budget_max"] = 200
        elif "under 500" in ql:
            filters["budget_max"] = 500
        elif "under 100" in ql:
            filters["budget_max"] = 100
            
        for d in ["biryani", "kebab", "pizza", "burger", "coffee", "roll", "chaat"]:
            if d in ql:
                filters["dish"] = d
                break
                
        if "near" in ql or "close" in ql:
            filters["max_distance_km"] = 5
            
        if "delivery" in ql:
            filters["delivery"] = True
            
        if "late night" in ql or "late-night" in ql:
            filters["vibe"] = "late-night"
        if "date" in ql or "romantic" in ql:
            filters["vibe"] = "date-night"
        if "study" in ql or "cafe" in ql:
            filters["vibe"] = "study-cafe"
            
        return filters

    def process_chat(self, query: str, history: List[Dict[str, str]]):
        """Process chat query and return generated reply and relevant restaurants."""
        # 1. Pre-filtering based on DB mapping
        filters = self.parse_filters(query)
        db_results = self.db.search(**filters, top_n=5)
        
        # 2. Semantic search
        query_embedding = self.embed_model.encode(query).tolist()
        vector_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )
        
        # 3. Merge and deduplicate
        db_ids = {r.id for r in db_results}
        merged_ids = list(db_ids)
        
        if vector_results and vector_results['ids'] and len(vector_results['ids'][0]) > 0:
            for vid in vector_results['ids'][0]:
                if vid not in db_ids:
                    merged_ids.append(vid)
        
        # Get final unique set of top 5
        final_restaurants = []
        for rid in merged_ids[:5]:
            r = self.db.get_by_id(rid)
            if r:
                final_restaurants.append(r)
                
        # 4. Generate with Gemini
        context_text = "\n\n".join([r.to_rag_text() for r in final_restaurants])
        if final_restaurants:
            prompt = f"User Query: {query}\n\nAvailable Context Restaurants:\n{context_text}\n\nUse ONLY the context to answer."
        else:
            prompt = f"User Query: {query}\n\nNo restaurants match the criteria completely. Let them know nicely."

        gemini_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        gemini_history.append({"role": "user", "parts": [prompt]})
        
        # Safety check if api key is mock
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            reply = "I apologize, but my Gemini API key has not been set yet, so I cannot generate a response. However, I did find these restaurants for you!"
        else:
            try:
                response = self.model.generate_content(gemini_history)
                reply = response.text
            except Exception as e:
                # Fallback if something goes wrong with gemini history format
                try:
                    response = self.model.generate_content(prompt)
                    reply = response.text
                except Exception as eval_e:
                    reply = f"Error generating response: {eval_e}"

        return {
            "reply": reply,
            "restaurants": final_restaurants
        }
