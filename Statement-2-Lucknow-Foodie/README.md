# 🍜 IIITL Food Scout: Context-Aware Recommendation Engine

**IIITL Food Scout** is a Retrieval-Augmented Generation (RAG) system designed to help students at IIIT Lucknow find the best local eateries. From budget-friendly dhabas in Arjunganj to high-end cafes in Phoenix Palassio, the Scout provides personalized recommendations with "student-first" logic.

## 🚀 Key Features
- **Smart Filtering:** Handles queries based on budget ("Broke student"), vibe ("Date night"), or specific cravings ("Best basket chaat").
- **Free-Tier Architecture:** Uses `HuggingFace` local embeddings and `Groq` for lightning-fast, zero-cost inference.
- **Context Awareness:** Specialized knowledge of the Ahmamau/Sultanpur Road area near the IIIT Lucknow campus.

---

## 🏗️ Project Workflow

### 1. Data Ingestion & Invisibility
- **Source:** Curated dataset of 50+ local restaurants in `dataset/lucknow_eateries.csv`.
- **Processing:** `engine.py` loads the CSV using LangChain's `CSVLoader`.

### 2. Hybrid Knowledge (Vectorization)
- **Embeddings:** Text is converted into vectors using the `all-MiniLM-L6-v2` model from HuggingFace (runs locally on CPU).
- **Storage:** Vectors are stored in a persistent `ChromaDB` instance (`food_index_db`) for high-speed semantic search.

### 3. RAG Orchestration & Frontend
- **Retriever:** When a student asks a question, the system finds the 3 most relevant restaurant entries.
- **Inference:** The context + query is sent to **Llama 3.3-70b via Groq**, ensuring answers are generated in under 1 second.
- **UI:** A sleek, interactive chat interface built with **Streamlit**.

---

## 📂 Directory Structure
```text
Statement-2-Lucknow-Foodie/
├── dataset/
│   └── lucknow_eateries.csv      # Scraped/Curated restaurant data
├── src/
│   ├── app.py                   # Streamlit Frontend & RAG Chain
│   ├── engine.py                # Data Ingestion & Embedding Script
└── README.md                    # Project Documentation

---

## Environment Setup

Follow the steps mentioned in the project README.md to create a virtual environment and install the required dependencies then run the following commands:

Bash

```
cd Statement-2-Lucknow-Foodie/src

# Run the backend
python engine.py

# Run the frontend
streamlit run app.py

```

## 🕹️ How to Use the FoodScout Assistant
Once the Streamlit interface is running, follow these steps to explore the Lucknow food scene:

Select your Vibe: Use the search bar to describe exactly what you are craving. You don't need exact restaurant names—describe the food or the mood (e.g., "Budget-friendly dinner in Hazratganj").

Test the Hybrid Search: Try queries that mix specific items with general locations. The engine uses Vector Search to understand "vibe" and Keyword Matching for specific locations.

Try: "Best Galouti Kebab near Aminabad"

Check for 'Hidden Gems': Ask for specific categories like "Pure Veg," "Street Food," or "Late Night" to see how the bot filters the dataset.

Analyze the Logic: Notice how the bot provides a reason why it recommended a place, pulling details directly from the restaurant dataset.

Reset & Refine: If you want to start a new search, use the "Clear Chat" button in the sidebar to refresh the context.
