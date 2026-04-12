# 🛡️ Statement-1: TITAN SECURE Insurance Decoder

## 📌 Project Overview
The **TITAN SECURE Insurance Decoder** is a Retrieval-Augmented Generation (RAG) AI assistant designed to strictly and accurately answer user queries regarding the Tier-1 Individual Platinum health insurance policy. It guarantees highly precise, formatted responses with direct section citations, eliminating AI hallucinations and conversational filler.

## ⚙️ Workflow
The system operates on a locally hosted, heavily optimized RAG pipeline:
1. **Document Ingestion:** The `TITAN SECURE.pdf` is loaded using LangChain's `PyPDFLoader`.
2. **Chunking:** Text is split using `RecursiveCharacterTextSplitter` (chunk size: 1000, overlap: 200) to ensure complete contextual sentences are preserved.
3. **Embedding & Storage:** Chunks are embedded using `sentence-transformers/all-MiniLM-L6-v2` and persistently stored in a local `Chroma_DB` vector database.
4. **Retrieval:** When a user asks a question, the system fetches the most relevant and diverse chunks of the policy to feed to the AI.
5. **Generation:** A meticulously prompted `meta-llama/Llama-3.1-8B-Instruct` model (running via HuggingFace Endpoint at a strict `temperature=0.01`) processes the context and returns a strictly formatted answer citing the exact policy section.


## BONUS
-->> implemented MMR retrieval for diverse context
-->> added caching to eliminate LLM and DB reload latency
-->> applied strict zero-creativity temperature protocol.


## Creative Features
-->>  💅 Custom UI/UX Theming: Bypassed default Streamlit styling by injecting custom CSS and a .streamlit/config.toml file to create a branded "Titan Secure" experience. This includes a corporate dark-mode palette, iOS-style rounded chat bubbles, floating shadows, and gradient-styled header typography.

-->>  🛡️ Anti-Hallucination Prompt Engineering: Designed a rigid ChatPromptTemplate utilizing Few-Shot examples that forces the AI to reply in a highly specific, cited format (e.g., "40% penalty on the claim, per Section 2.2"), dropping all conversational AI filler.



## 🚀 How to Run Locally

### 1. Prerequisites
Ensure you have Python 3.9+ installed. You will also need a HuggingFace API key.

### 2. Setup
Create a `.env` file in the root directory and add your API key:
env
HUGGINGFACEHUB_API_TOKEN={your_api_key_here }

### 3. Installation
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt

### 4. Database Craetion & Launch APP
python src/database.py
streamlit run src/app.py



