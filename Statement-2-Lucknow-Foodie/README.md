# Statement 2 - Lucknow Foodie Guide (40 pts)

Build a context-aware restaurant recommendation engine for Lucknow focused around **IIIT Lucknow**, using **Hybrid Retrieval + Filters + RAG-style answer generation**.

---

## What this project does

- Loads a curated dataset of **30+ Lucknow eateries**
- Supports **natural language queries** like:
  - "budget biryani near IIIT Lucknow"
  - "best basket chaat in Hazratganj"
  - "quiet cafe near campus"
- Uses **hybrid retrieval**:
  - **Semantic search** with Sentence Transformers embeddings
  - **Keyword match** across restaurant fields
- Applies **smart filters**:
  - budget (max price for two), rating threshold
  - veg / non-veg (includes "Both" appropriately)
  - vibe, dish, area hint
  - near-IIIT using `distance_from_iiit_km`
- Generates a concise response using a **local lightweight LLM** (`google/flan-t5-small`) with a deterministic fallback summary if the model output is poor.

---

## Repository structure

```
Statement-2-Lucknow-Foodie/
├── dataset/
│   └── restaurants.csv
└── src/
    ├── app.py
    ├── frontend_streamlit.py
    ├── data_loader.py
    ├── query_understanding.py
    ├── keyword_search.py
    ├── semantic_search.py
    ├── hybrid_search.py
    ├── rag_llm.py
    └── rag_response.py
```

---

## Dataset

File: `dataset/restaurants.csv`

### Columns

- `name`: restaurant name
- `location`: area (e.g., Gomti Nagar, Hazratganj, Chowk, Phoenix Palassio, Sushant Golf City)
- `cuisine`: cuisine type
- `rating`: numeric rating (0-5)
- `price_for_two`: approximate cost for two in INR
- `signature_dish`: must-try item(s)
- `veg_nonveg`: `Veg` / `Non-Veg` / `Both`
- `vibe`: tags like `Cafe`, `Street`, `Family`, `Rooftop`, `Premium`, `Luxury`
- `hours`: opening hours text (e.g., `11:00-23:00`)
- `distance_from_iiit_km`: approximate distance from IIIT Lucknow (used for near-campus queries)

> Note: Distances are approximate and intended for filtering + ranking (not for navigation).

---

## Architecture (Hybrid RAG)

1. **Query understanding** (`src/query_understanding.py`)
   - Extracts filters from user text (budget, rating, veg/non-veg, vibe, dish, near-IIIT intent).

2. **Retrieval**
   - **Semantic retrieval** (`src/semantic_search.py`): Sentence Transformers similarity over combined text fields.
   - **Keyword retrieval** (`src/keyword_search.py`): substring matches on name/cuisine/location/signature dish.
   - **Hybrid ranking** (`src/hybrid_search.py`): weighted score + filter application + safe fallbacks (relax dish/near-IIIT radius if needed).

3. **Answer generation**
   - **Local LLM** (`src/rag_llm.py`): formats top candidates into a context prompt and produces 2-3 recommendations.
   - Includes a **fallback renderer** when the small model output is irrelevant.

---

## Tech stack

- Python
- `pandas`, `numpy`
- `sentence-transformers` for embeddings
- `transformers` + `torch` for local LLM generation (`flan-t5-small`)
- `streamlit` for frontend UI

---

## Setup

From repo root:

```bash
python -m venv venv
.\venv\Scripts\activate    # Windows PowerShell
pip install -r Statement-2-Lucknow-Foodie/requirements.txt
```

> Optional: HuggingFace downloads run faster with `HF_TOKEN` set, but it is not required.

---

## Run (CLI)

```bash
python Statement-2-Lucknow-Foodie/src/app.py
```

---

## Run (Frontend)

From repo root:

```bash
streamlit run Statement-2-Lucknow-Foodie/src/frontend_streamlit.py
```

If you are already inside `Statement-2-Lucknow-Foodie/src`:

```bash
streamlit run .\frontend_streamlit.py
```

---

## Example queries

- "Suggest a budget-friendly biryani place near IIIT Lucknow under 500"
- "Best basket chaat in Hazratganj"
- "Premium rooftop dinner near campus"
- "Veg cafe near Palassio with rating above 4"

---

## Creative features

- **UI/UX**: Streamlit frontend with modern cards, badges, presets, sort options, and table view.
- **Robustness**: fallback recommendation formatting when the local small LLM output is weak.
- **Near-campus ranking**: distance-aware filtering with adjustable radius.

