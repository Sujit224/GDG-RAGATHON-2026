# PlacementIQ: AI-Powered Placement Predictor & Mentorship System

PlacementIQ is a comprehensive, AI-driven placement readiness platform that evaluates student profiles, calculates a precise readiness score, and provides highly personalized mentorship by semantically matching students with relevant senior interview experiences. 

By unifying a **Conversational AI Profiler**, **Machine Learning Regression Models**, and a **Retrieval-Augmented Generation (RAG) Engine**, PlacementIQ delivers an end-to-end preparation hub for students gearing up for technical placements.

## 🚀 System Architecture (RAG Pipeline)

Our RAG engine extracts unstructured `.pdf` logs, chunks them efficiently, and implements advanced vector search.
* **Document Extraction:** Uses Python regex parsing and document readers to clean unstructured text from PDF/DOCX logs.
* **Chunking:** `Regex-based line splitting` to divide distinct Interview Experiences into contextual chunks.
* **Embeddings:** `HuggingFace sentence-transformers` (`all-MiniLM-L6-v2`) generates deep semantic embeddings for the tech stack and project profile of the student against the corpus tokens.
* **Vector Store & Retrieval:** `FAISS-CPU` Local Flat L2 Indexing for hyper-fast latency retrieval. Retrieves the Top 'K' matches scored against Euclidean distance translated to a percentage certainty.
* **Generation:** `Gemini 2.0 Flash` formulates human-readable extraction mappings and gracefully translates vector responses to semantic cards.

## 📈 Regression Metrics (Statement 3)
For the prediction of precisely scored readiness, a Random Forest was trained on a synthesized dataset matching the academic schema.

* **Model Used:** `RandomForestRegressor(n_estimators=100, random_state=42)` from `Scikit-Learn`.
* **Performance Metrics:**
  * **R² Score:** `0.8765` (High variance explanation, proving strong correlations between features like DSA and GitHub commits to the final Score).
  * **Mean Squared Error (MSE):** `9.3655`

## 📁 Folder Structure

```text
Statement-3-Placement-Predictor/
├── data/                             # Datasets, saved embeddings, and ML models
│   ├── INTERVIEW EXPERIENCES.pdf     # Source corpus for RAG
│   ├── faiss_index.bin               # Local fast vector database
│   ├── model.pkl                     # Saved RandomForestRegressor model
│   └── normalized_placement_data.csv # Training data for metrics
├── frontend/                         # User Interface Layer (HTML/CSS/JS)
│   ├── app.js
│   ├── index.html
│   └── styles.css
├── src/                              # Core Python logical backends
│   ├── main.py                       # FastAPI application entrypoint
│   ├── models.py                     # Pydantic data structures
│   ├── profiler.py                   # Chatbot conversation state logic
│   ├── rag_engine.py                 # Vector DB / Embeddings generator
│   ├── regression_engine.py          # Machine learning readiness scorer
│   └── resume_parser.py              # GenAI PDF to Schema extractor
├── .env.example
├── requirements.txt
└── README.md
```

## ⚙️ Setup Instructions

### 1. Prerequisites
Ensure you have Python `3.11+` installed on your machine.

### 2. Prepare Environment Variables
Copy the `.env.example` file to create your own configuration:
```bash
cp .env.example .env
```
Inside `.env`, insert your verified Gemini API key:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

### 3. Installation
```bash
# Set up a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Start the Application
Run the FastAPI application as a module from the root path:
```bash
python -m src.main
```
The server will bind dynamically to port `8000`. Navigate to `http://localhost:8000` to test the frontend web application.

---

## 🌟 Bonus Tasks & Extra Features Completed
We went above and beyond the baseline requirements:

* **✅ File Upload Support:** Full support for automated resume parsing (PDFs and DOCX).
* **✅ Explorable Dashboard (UI):** Delivered a sleek, premium frontend that visualizes the Readiness Score on an animated gauge.
* **✅ Fully Functional Chatbot Interface:** Built a stateful chat-sync interface in the UI, ensuring smooth profiling interactions.
* **✅ API Rate Limit Resilience (Custom Extra):** Built custom heuristic arithmetic fallbacks ensuring the app never crashes under an API `429 Quota Exceeded` penalty.
* **✅ High-Performance Local Vector Store (Custom Extra):** Replaced slow off-board vector lookups with a locally saved `faiss-cpu` index for instant senior experience matching.


## LINK
https://youtu.be/6l70OrPNs58
