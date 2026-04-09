# ⚖️ Fine Print Decoder (Statement 1)

---

## 🎯 Overview

The **Fine Print Decoder** is a high-stakes RAG (Retrieval-Augmented Generation) system designed to simplify complex legal jargon found in policy documents. 

While primarily optimized for the **Titan Secure Health Insurance Policy**, the system features a modular multi-document architecture that can ingest and decode any legal contract (Loans, Rentals, etc.) in real-time.

---

## ✨ Key Features

* **ELI5 Simplification:** Converts dense legal "fine print" into easy-to-understand language for everyday users.
* **Bonus Citation Engine:** Automatically identifies and cites **Section numbers, Clause numbers, and Page numbers** for 100% transparency.
* **Dynamic Multi-Doc RAG:** Ingests multiple PDFs simultaneously from a local directory or via the Web UI.
* **Interactive Web Interface:** A professional Streamlit UI with chat history and real-time re-indexing.
* **High-Stakes Accuracy:** Uses `gemini-1.5-flash-lite` to ensure fast, accurate, and quota-resilient responses.

---

## 🛠️ Tech Stack

* **LLM:** Google Gemini (`gemini-1.5-flash-lite-latest`)
* **Embeddings:** `models/gemini-embedding-001`
* **Orchestration:** LangChain & LangChain-Classic
* **Vector Database:** ChromaDB
* **Frontend:** Streamlit

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have a `.env` file in the root directory with your Google API Key:
```env
GOOGLE_API_KEY=your_api_key_here