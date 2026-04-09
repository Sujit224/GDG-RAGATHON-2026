# The Lucknow Foodie Guide (Statement 2)

This module implements a **Hybrid Search** recommender for local eateries around Lucknow using dense vectors + hard metadata filters.

## Files

- `dataset/restaurants.json`  
  Sample data for 5 eateries with:
  - `name`
  - `vibe`
  - `budget`
  - `signature_dishes`
  - `is_veg`
  - `reviews`

- `src/hybrid_search.py`  
  Python pipeline using **Qdrant** for vector storage and metadata filtering.

## Hybrid Search Logic

The recommender combines two retrieval strategies:

1. **Dense Vector Search (semantic)**
   - Embeds restaurant text using `all-MiniLM-L6-v2`.
   - Captures vibe and intent similarity (e.g., "cozy", "authentic", "youth crowd").

2. **Hard Metadata Filtering**
   - Applies strict filters in Qdrant for:
     - `budget` (e.g., `budget`, `mid`, `premium`)
     - `is_veg` (`true`/`false`)
   - Ensures business constraints are respected even if semantic matches are broad.

This makes recommendations both **relevant** and **constraint-compliant**.

## Usage

From repository root:

```bash
python Statement-2-Lucknow-Foodie/src/hybrid_search.py
```

Programmatic example:

```python
from Statement-2-Lucknow-Foodie.src.hybrid_search import suggest_places

results = suggest_places(
    query="Suggest a budget-friendly Biryani place",
    budget="budget",
    is_veg=False,
    limit=3,
)
```
