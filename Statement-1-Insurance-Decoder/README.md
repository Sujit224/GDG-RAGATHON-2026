# Fine Print Decoder: Titan Secure Health Insurance Assistant
GDG RAGATHON 2026 Submission

🎯 Project Overview
The Fine Print Decoder is a specialized Retrieval-Augmented Generation (RAG) system designed to demystify complex legal jargon found in insurance policies and contracts. It transforms high-stakes, confusing policy documents into "ELI5" (Explain Like I'm Five) explanations while maintaining 100% accuracy through direct source attribution.

## Problem Statement
Insurance policies are often filled with hidden clauses and complex legal language. Our goal was to build a bot that:

Ingests official policy documents.

Filters information based on specific user categories (coverage, penalties, exclusions).

Provides simple explanations cited with exact Section and Page references.

## 🛠️ Tech Stack
Frontend: Streamlit

Orchestration: LangChain

LLM: Llama 3.3 70B (via Groq Cloud)

Vector Database: ChromaDB

Embeddings: HuggingFace (all-MiniLM-L6-v2)

Document Loading: PyPDF

## ⚙️ Workflow
Context Loading: The system uses PyPDFLoader to ingest the TITAN SECURE.pdf policy document.

Smart Splitting: Documents are broken into 800-character chunks with a 100-character overlap using RecursiveCharacterTextSplitter to ensure no context is lost between chunks.

Vectorization: Chunks are converted into vector embeddings using a local HuggingFace model and stored in a persistent ChromaDB instance.

Retrieval & Hybrid Knowledge: When a user asks a question (e.g., "Does this cover extreme sports?"), the system retrieves the top 3 most relevant snippets.

ELI5 Synthesis: The Groq-hosted Llama 3.3 model processes the snippets and generates a simplified response strictly following the "Fine Print Decoder" prompt template, ensuring every answer includes a Legal Source citation.

🚀 Getting Started
Prerequisites
Python 3.9+

A Groq Cloud API Key

Installation
Clone the repository:

Bash
```
git clone <your-fork-url>
cd GDG-RAGATHON-2026
```
Set up a virtual environment:

Bash
```
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```
Install dependencies:

Bash
```
pip install -r requirements.txt
```
Environment Variables:
Create a .env file in the root directory and add your Groq API key:

Code snippet
```
GROQ_API_KEY=your_actual_key_here
```
Running the Application
To launch the Streamlit interface:

Bash
```
streamlit run app.py
```
📁 Project Structure
app.py: The Streamlit frontend and chat interface logic.

main.py: The core RAG pipeline, including document loading, embedding, and chain construction.

docs/: Directory containing the policy PDFs (e.g., TITAN SECURE.pdf).

chroma_db/: Local persistent storage for vector embeddings.

🏆 Bonus Features Implemented
Source Attribution: Every response explicitly cites the Section Name/Clause Number and the Page Number to ensure transparency and trust.

ELI5 Formatting: Uses a custom system prompt to force the LLM to explain legal concepts in a way that is accessible to everyone.

Resource Caching: Implements @st.cache_resource to prevent reloading the PDF and Embeddings on every user interaction, ensuring a fast UI experience.