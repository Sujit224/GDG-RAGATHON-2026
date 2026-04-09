# Lucknow Foodie Guide

A context-aware restaurant recommendation chatbot for students of IIIT Lucknow built with React, FastAPI, RAG, and Gemini.

## Prerequisites

- Node.js (v18+)
- Python 3.10+
- Free Gemini API Key (get from [AI Studio](https://aistudio.google.com/app/apikey))

## Getting Started

### 1. Backend Setup

Open a terminal and navigate to the project root:

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate   # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
👉 **IMPORTANT**: Open `backend/.env` and add your `GEMINI_API_KEY`.

Start the backend server (FastAPI):
```bash
uvicorn main:app --reload --port 8000
```


### 2. Frontend Setup

Open a **new** terminal and navigate to the project root:

```bash
cd frontend
npm install
npm run dev
```

👉 **Open** http://localhost:5173 in your browser to view the app!

## Features
- **Local Embedded Search:** ChromaDB + SentenceTransformers locally powers RAG embeddings with no external API dependency except Generation.
- **Smart Filters:** Instantly slice the data by Diet, Vibe, Budget, and Area.
- **Gemini Chat:** Native query resolution directly context-aware via RAG vectors.
- **Interactive Map:** Free OpenStreetMaps and Leaflet dynamically track restaurant locations referenced in Chat or List.
