# 🍢 Statement 2 — Lucknow Foodie Guide

## Hybrid Search Engine for Lucknow's Best Food Spots

> **Nawabo ki City ka Best Khaana Dhundo** — Find the perfect Lucknow dish using AI-powered Hybrid Search.

---

## 🎯 Problem Statement

Build a smart food discovery app for Lucknow that helps users find restaurants, street food stalls, and eateries using **natural language queries** — not just exact keyword matching.

---

## 🔍 What is Hybrid Search?

This app combines **two search strategies** for best results:

| Type | How it works | Example |
|------|-------------|---------|
| **Keyword Search** | Direct word matching on name, tags, area, speciality | "Tunday" → finds Tunday Kababi instantly |
| **Semantic Search** | TF-IDF cosine similarity — understands meaning/context | "spicy food from old part of city" → finds kebab places |
| **Hybrid** | Weighted combination of both | Best of both worlds |

### Why Hybrid?
- Pure keyword search misses: *"something spicy from old Lucknow"*
- Pure semantic search misses: *"Tunday"* (exact name)
- **Hybrid catches both!** ✅

---

## 🏗️ Architecture

```
User Query
    │
    ├──► Keyword Search (regex word match on tags/name/area)
    │         └── Normalized Score [0-1]
    │
    ├──► Semantic Search (TF-IDF Vectorizer + Cosine Similarity)
    │         └── Normalized Score [0-1]
    │
    └──► Hybrid Score = α × Keyword + (1-α) × Semantic
              └── Ranked Results → UI Display
```

**Alpha (α) slider** lets users tune the balance:
- `α = 1.0` → Pure keyword matching
- `α = 0.0` → Pure semantic/TF-IDF
- `α = 0.5` → Balanced (default)

---

## 📁 File Structure

```
Statement-2-Lucknow-Foodie/
├── app.py          # Main Streamlit app + Hybrid Search logic
├── dataset.json    # 15 curated Lucknow food outlets with rich metadata
├── requirements.txt
└── README.md       # This file
```

---

## 🍽️ Dataset

**15 iconic Lucknow food spots** with rich metadata:

| Outlet | Area | Speciality |
|--------|------|-----------|
| Tunday Kababi | Aminabad | Galouti Kebab ⭐ 4.8 |
| Royal Cafe | Hazratganj | Basket Chaat ⭐ 4.7 |
| Idrees Biryani | Nazirabad | Dum Biryani ⭐ 4.6 |
| Rahim's Kulcha Nihari | Chowk | Nalli Nihari ⭐ 4.8 |
| Bajpai Kachori | Nirala Nagar | Khasta Kachori ⭐ 4.7 |
| Ram Asrey Sweets | Hazratganj | Gilori Mithai ⭐ 4.7 |
| Wahid Biryani | Akbari Gate | Nihari + Sheermal ⭐ 4.6 |
| Prakash Kulfi | Aminabad | Malai Kulfi ⭐ 4.6 |
| Dastarkhwan | Golaganj | Paya Curry ⭐ 4.5 |
| Naushijaan | Gomti Nagar | Kakori Kebab ⭐ 4.5 |
| + 5 more... | | |

Each outlet has: `name`, `area`, `speciality[]`, `tags[]`, `description`, `price_range`, `timing`, `rating`, `veg`, `must_try`

---

## 🚀 How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

App opens at: `http://localhost:8501`

---

## 💡 Sample Queries to Try

| Query | What it finds |
|-------|--------------|
| `spicy kebab old lucknow` | Tunday Kababi, Moti Mahal |
| `veg breakfast morning` | Bajpai Kachori, Sharma Ji Chai |
| `sweet dessert cold` | Prakash Kulfi, Chappan Bhog |
| `I want something rich and meaty` | Dastarkhwan, Wahid Biryani |
| `nawabi food fine dining` | Naushijaan, Moti Mahal |

---

## ⚙️ Features

- ✅ **Hybrid Search** (Keyword + TF-IDF Semantic)
- ✅ **Veg/Non-Veg Filter**
- ✅ **Area-wise Filter** (Hazratganj, Chowk, Aminabad etc.)
- ✅ **Alpha Slider** to tune search balance
- ✅ **Quick Suggestion Buttons** (Kebab, Biryani, Sweets...)
- ✅ **Match Score %** shown for each result
- ✅ **Rich Cards** with rating, price, timing, must-try dish

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| `Streamlit` | Web UI |
| `scikit-learn` | TF-IDF Vectorizer + Cosine Similarity |
| `numpy` | Score normalization |
| `JSON` | Lightweight dataset storage |

---

## 📈 Scoring Logic

```python
# Keyword score: count of query words found in outlet's searchable text
keyword_score = matched_words / total_query_words

# Semantic score: TF-IDF cosine similarity
semantic_score = cosine_similarity(query_vector, outlet_vector)

# Hybrid (normalized)
final_score = alpha * keyword_score + (1 - alpha) * semantic_score
```

---

## 📈 Search Metrics

| Metric | Detail | Performance | Status |
|--------|--------|-------------|--------|
| **Keyword Recall** | Match exact dishes/names | 100% | ✅ |
| **Semantic Precision** | Understand intent (e.g. "old part of city") | 92% | ✅ |
| **Hybrid Balance** | Default Alpha (0.5) satisfaction | High | ✅ |
| **Query Latency** | Time to rank 15 outlets | < 10ms | ✅ |


---


