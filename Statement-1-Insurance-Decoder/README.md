# Statement 1: Insurance Decoder

An intelligent, full-stack Retrieval-Augmented Generation (RAG) system built to decode, analyze, and explain complex insurance policies with high precision.

## 🏛️ Architecture

Our application is structured around a decoupled yet integrated architecture consisting of an AI-powered extraction backend and a visually appealing, fast client interface:

1. **Embedding & Vector Store**: Policies (PDFs) are ingested using `PyPDFLoader`, split into chunks through LangChain's `RecursiveCharacterTextSplitter`, and embedded seamlessly utilizing a HuggingFace Sentence Transformer (`all-MiniLM-L6-v2`) inside a local `FAISS` vector database.
2. **Retrieval Pipeline (`rag.py`)**: For each user query, `FAISS` retrieves the top 4 most pertinent documents. A context block is dynamically assembled and fed alongside the query to the `Gemini 1.5 Flash` LLM.
3. **Backend API (`app.py`)**: A `FastAPI` instance serves as the bridge between the RAG pipeline and the frontend, exposing a `/api/ask` endpoint and mounting the static frontend folder.
4. **Client Interface (`frontend/`)**: A sleek, vanilla HTML/CSS/JS frontend styled with modern UI paradigms like glassmorphism to interact with the backend API.

## 🛠️ Tech Stack

### AI & Backend Pipeline
- **RAG & Chunking:** LangChain (`langchain-community`, `langchain-text-splitters`)
- **Embeddings:** HuggingFace `all-MiniLM-L6-v2`
- **Vector Database:** FAISS CPU
- **LLM:** Google Gemini (`gemini-1.5-flash`)
- **API Framework:** FastAPI, Uvicorn

### Frontend
- **Structure:** Vanilla HTML5
- **Styling:** Vanilla CSS3 (Custom Properties, Flexbox, Glassmorphism effects)
- **Logic / AJAX:** Vanilla JavaScript (`fetch` API)
- **Icons:** BoxIcons

---

## 🌟 Bonus implementation

### (+5 Points) Explicit Source Attribution

We successfully implemented the bonus requirement for source attribution. 
- **Methodology:** The system prompts the LLM via stringent instructions to autonomously locate and output the exact `Section` and `Clause` numbers referenced in its generated response.
- **Output Validation:** The backend parser enforces that Gemini's response string is validated as strict JSON. We extract the array of "citations" natively and render them on the user interface as official citation badges.

---

## 🚀 Running the Project

1. Navigate to the root folder of the repository.
2. **Activate the Virtual Environment**: You must run the server from within the virtual environment where your dependencies (`requirements.txt`) are installed.
   - **Windows:** `.\venv\Scripts\activate` or `venv\Scripts\activate`
   - **Mac/Linux:** `source venv/bin/activate`
3. If you haven't already, install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Change directory into the `src` folder of Statement 1:
   ```bash
   cd Statement-1-Insurance-Decoder/src
   ```
5. Start the FastAPI server by running:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
6. Open your browser and navigate to `http://localhost:8000` to interact with the Assistant UI!
