# 🍽️ Lucknow Foodie Guide: IIITL Edition

Welcome to the **Lucknow Foodie Guide**, an intelligent, context-aware recommendation engine designed specifically for the students of IIIT Lucknow. This bot leverages **RAG (Retrieval-Augmented Generation)** to help you navigate the local food scene, from the historic lanes of Chowk to the modern cafes in Phoenix Palassio.

---

## 🌟 Bonus Tasks Completed!
> **Hybrid Knowledge & Smart Filtering Achieved:**  
> We have successfully completed all bonus tasks and advanced implementations! The bot uses hybrid RAG knowledge to retrieve intricate restaurant details like hours, signature dishes, and exact locations while filtering intelligently based on vibes, budget, and dietary preferences. In addition, explicit source provenance has been included in our answers for absolute transparency!

---

## 🏗️ System Architecture
The project implements a modular RAG pipeline to ensure high-precision recommendations based on a curated local dataset:

1. **Context Loading**: A structured `restaurants.json` file containing details for 30+ local eateries.
2. **Chunking**: The data is processed using a `RecursiveCharacterTextSplitter` (Chunk Size: 500, Overlap: 50) to maintain the integrity of restaurant profiles.
3. **Embeddings**: Text chunks are transformed into numerical vectors using OpenAI Embeddings (`text-embedding-3-small`).
4. **Vector Store**: Vectors are indexed and stored using **FAISS** (Facebook AI Similarity Search) for rapid semantic retrieval.
5. **Generation**: When a user queries the bot, the system retrieves the most relevant restaurant data and uses an LLM to synthesize a helpful, "vibe-checked" response.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9 or higher
- An active OpenAI API Key

### 2. Environment Configuration
Create a `.env` file in the project directory:
```bash
OPENAI_API_KEY=your_api_key_here
```

### 3. Installation
Navigate to the project directory and install the necessary dependencies:
```bash
cd Statement-2-Lucknow-Foodie
pip install langchain openai faiss-cpu python-dotenv
```

### 4. Running the Project

**Step 1: Data Ingestion**
Run the ingestion script to process the `restaurants.json` file and create the FAISS vector database.
```bash
python3 src/ingest.py
```

**Step 2: Start the Engine**
Run the main script directly to start interacting with the local food guide:
```bash
python3 src/main.py
```

---

## 💡 Usage Examples

- **Vibe-based**: *"Where can I find a chill cafe to study near IIITL?"*
- **Budget-focused**: *"Suggest a budget-friendly Biryani spot in Gomti Nagar."*
- **Dish-specific**: *"Who serves the best Basket Chaat around here?"*
- **Dietary**: *"Find me the best non-veg kebabs in the city."*

---

## 📁 Folder Structure

```text
RAGATHON/
└── Statement-2-Lucknow-Foodie/
    ├── dataset/
    │   ├── .gitkeep
    │   └── restaurants.json
    ├── src/
    │   ├── .gitkeep
    │   ├── ingest.py
    │   └── main.py
    ├── static/
    │   ├── images/
    │   ├── app.js
    │   ├── index.html
    │   └── styles.css
    ├── .env.example
    ├── .gitkeep
    └── run.sh
```
## 🎥 Video Link
Check out the system in action: **[Watch Video](https://www.youtube.com/watch?v=W8XDQALeczM)**