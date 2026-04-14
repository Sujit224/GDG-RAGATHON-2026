# 🍕 Statement 2 — Lucknow Foodie Guide

> A context-aware, RAG-powered restaurant recommendation chatbot for IIIT Lucknow students.

## 🏗️ System Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Chat UI     │────▶│  FastAPI Server   │────▶│  Hybrid Search  │
│  (HTML/JS)   │◀────│  (app.py)         │◀────│  (rag.py)       │
└──────────────┘     └──────────────────┘     └────────┬────────┘
                                                        │
                              ┌──────────────────────────┼──────────────────┐
                              ▼                          ▼                  ▼
                     ┌────────────────┐       ┌──────────────────┐  ┌──────────────┐
                     │ Keyword Filter │       │ ChromaDB Vector  │  │  Groq LLM    │
                     │ (veg, budget,  │       │ Search (cosine   │  │  (llama-3.3  │
                     │  nearby, vibe) │       │  similarity)     │  │  -70b)       │
                     └────────────────┘       └──────────────────┘  └──────────────┘
                                                        ▲
                                               ┌────────┴────────┐
                                               │  Ingestion      │
                                               │  (ingest.py)    │
                                               │  sentence-      │
                                               │  transformers   │
                                               └────────┬────────┘
                                                        ▲
                                               ┌────────┴────────┐
                                               │ restaurants.json│
                                               │ (41 eateries)   │
                                               └─────────────────┘
```

### RAG Pipeline

1. **Ingestion** (`src/ingest.py`):
   - Loads 41 restaurants from `dataset/restaurants.json`
   - Converts each to a rich-text document combining all attributes
   - Embeds using `sentence-transformers` (`all-MiniLM-L6-v2`) — runs locally, no API key
   - Stores in local ChromaDB with cosine similarity indexing

2. **Hybrid Search** (`src/rag.py`):
   - **Keyword Pre-filtering**: Extracts intent from query (veg/non-veg, budget/premium, nearby, vibe)
   - **Semantic Vector Search**: ChromaDB cosine similarity finds relevant restaurants
   - **LLM Generation**: Groq (LLaMA 3.3 70B) generates conversational responses from retrieved context
   - **Conversation Memory**: Maintains last 6 turns for follow-up queries

3. **API Server** (`src/app.py`):
   - FastAPI backend with auto-ingestion on first startup
   - `POST /chat` — main conversational endpoint
   - `GET /restaurants` — browse all restaurants
   - `POST /reset` — clear chat history

4. **Frontend** (`src/static/index.html`):
   - Dark-themed chat UI with warm amber accents
   - Quick-action suggestion chips for common queries
   - Markdown rendering with restaurant cards
   - Responsive design for mobile and desktop

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| **LLM** | Groq (LLaMA 3.3 70B Versatile) |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) |
| **Vector DB** | ChromaDB (local, persistent) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JS |
| **Dataset** | Hand-curated JSON (41 Lucknow restaurants) |

---

## 🚀 Setup Instructions

### 1. Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Groq API key
```

Get a free Groq API key at: https://console.groq.com

### 2. Install Dependencies

```bash
# From the Statement-2-Lucknow-Foodie directory
pip install -r requirements.txt
```

### 3. Run the Server

```bash
# From the Statement-2-Lucknow-Foodie directory
uvicorn src.app:app --reload --port 8000
```

On first run, the server will **automatically**:
- Load the restaurant dataset
- Create embeddings (takes ~30 seconds)
- Store in ChromaDB

### 4. Open the Chat UI

Navigate to: **http://localhost:8000**

---

## 📂 Folder Structure

```
Statement-2-Lucknow-Foodie/
├── dataset/
│   └── restaurants.json         # 41 curated Lucknow restaurants
├── src/
│   ├── __init__.py
│   ├── ingest.py                # Embedding + ChromaDB ingestion
│   ├── rag.py                   # Hybrid search + Groq LLM
│   ├── app.py                   # FastAPI server
│   └── static/
│       └── index.html           # Chat UI
├── .env.example                 # API key template
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

---

## 💬 Example Queries

| Query | What it Tests |
|---|---|
| "Suggest a budget-friendly Biryani place near campus" | Budget filter + nearby + semantic search |
| "Where can I find the best basket chaat in Gomti Nagar?" | Semantic search + area matching |
| "Best date night spot with rooftop vibes" | Vibe-based filtering |
| "I want vegetarian food under ₹500" | Veg filter + price filter |
| "Late night food options near IIIT" | Time-based + proximity search |
| "Tell me about Tunday Kababi" | Direct restaurant lookup |

---

## 📊 Dataset Coverage

- **41 restaurants** across Lucknow (exceeds the 20-30 requirement)
- **Distance zones**: 0-1 km (campus), 1-5 km (Phoenix Palassio area), 5-10 km (Lulu Mall), 10+ km (heritage)
- **Cuisines**: Mughlai, North Indian, Street Food, Continental, Italian, Mexican, Arabic, and more
- **Price ranges**: ₹ (₹60-300) to ₹₹₹₹ (₹2000+)
- **Includes all explicitly named restaurants**: Tunday Kababi, Royal Cafe, Sky Glass Brewing, Phoenix Palassio cafes
