# 🍔 Statement-2: The IIITL Foodie Guide

## 📌 Project Overview
The **IIITL Foodie Guide** is an intelligent, context-aware restaurant recommendation engine built specifically for students in and around IIIT Lucknow. Instead of relying on static text searches, this bot utilizes a hybrid knowledge approach, combining semantic search with dynamic metadata filtering to find the perfect meal based on exact budget, dietary preferences, and distance constraints.

## ⚙️ Workflow
This project utilizes an advanced dual-LLM Retrieval-Augmented Generation (RAG) architecture:
1. **Context Loading:** A custom dataset (`lucknow_food.csv`) containing local eateries is parsed using Pandas. Searchable text (Vibe, Reviews, Signature Dishes) is separated from hard metadata (Budget, Is_Veg, Distance_km).
2. **Embedding & Storage:** The text is embedded using `sentence-transformers/all-MiniLM-L6-v2` and stored alongside its metadata in a local `ChromaDB` instance.
3. **Smart Filtering (Self-Querying):** A strict, low-temperature (`0.01`) LLM reads the user's natural language prompt, extracts logic (e.g., "under 300 rupees"), and dynamically writes ChromaDB metadata filters on the fly.
4. **Retrieval:** The filtered vector store returns the top semantic matches based on the user's requested "vibe" or specific cravings.
5. **Generation:** A second, higher-temperature (`0.4`) LLM processes the filtered context and generates a friendly, energetic, and highly personalized recommendation.


## BONUS FEATURES

-->> implemented caching for heavy components (Used @st.cache_resource to keep models loaded in memory, eliminating wait times between chat messages).

-->>  implemented SelfQueryRetriever (Upgraded from hardcoded filters to an LLM-driven query parser that dynamically translates natural language into database constraints)


## ✨ Creative Features
1. 🎨 "Foodie" Themed Web UI
        Streamlit is used to create a beautiful ui, we kept ui clean, fully working, and a little foodie enviornment

2. 🧠 Stateful Chat Memory
        The application utilizes Streamlit's session state to maintain a continuous chat history, allowing users to scroll back and review their previous recommendations without losing context.

3. 🎭 Persona-Driven Prompt Engineering
        The system prompt is rigorously engineered to adopt the persona of a friendly, knowledgeable senior student. It is instructed to explicitly extract 'Signature Dishes' and 'Vibe' from the CSV metadata to explain why the user should visit a spot, rather than just listing facts. It also includes an "Empty Context Fallback" to gracefully handle impossible queries (e.g., "Find me a 5-star restaurant for 10 rupees") without hallucinating.





## 🚀 How to Run Locally

### 1. Prerequisites
* Python 3.9 or higher
* A valid HuggingFace API key

### 2. Environment Setup
Create a `.env` file in the root directory and add your HuggingFace token:
"""env
HUGGINGFACEHUB_API_TOKEN=your_api_key_here"""

### 3. Installation
pip install -r requirements.txt

### 4. Database Setup
Make sure your lucknow_food.csv file is in the root directory. Run your database script once to initialize the Foodie_DB Chroma vector store.

### 5. Launch THE APP
streamlit run app.py
