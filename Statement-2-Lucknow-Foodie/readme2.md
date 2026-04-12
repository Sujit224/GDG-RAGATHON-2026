# 🍛 Lucknow Foodie Guide

> Your AI-powered food buddy near IIIT Lucknow

Lucknow Foodie Guide is a full-stack AI-powered restaurant recommendation system built specifically for students of IIIT Lucknow. It uses a **Retrieval-Augmented Generation (RAG)** pipeline to deliver smart, contextual, and conversational food suggestions.

---

## 🚀 Features

### 🤖 AI Chatbot (RAG Powered)
- Context-aware chatbot using Gemini 1.5 Flash
- Semantic search using sentence-transformers
- Local vector DB powered by ChromaDB
- Multi-turn conversation memory

### 🍽️ Smart Recommendations
- Budget-aware suggestions
- Diet filters (Veg / Non-Veg)
- Distance-based filtering (near campus)
- Dish-specific search (biryani, kebab, etc.)
- Mood-based recommendations (date, study, late-night)

### 🗺️ Interactive Map
- Built using Leaflet + OpenStreetMap
- Shows all recommended restaurants
- "You are here" marker (IIIT Lucknow)
- Clickable markers with details

### 🎛️ Advanced Filters
- Diet, Budget, Area, Sort options
- Real-time API-based filtering

### 💬 Modern Chat UI
- Inline restaurant cards in chat
- Quick suggestion chips
- Typing indicator
- Chat history persistence (localStorage)

---

## 🏗️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Axios
- React Leaflet
- Lucide React

### Backend
- FastAPI
- Google Gemini 1.5 Flash
- Sentence Transformers
- ChromaDB

---

## 📁 Project Structure

```
lucknow-foodie-guide/
├── backend/
│   ├── main.py
│   ├── rag_engine.py
│   ├── lucknow_foodie_data_utils.py
│   ├── lucknow_restaurants.json
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx
    │   ├── components/
    │   ├── hooks/
    │   └── api/
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## ⚙️ Setup Instructions

### 🔧 Backend Setup

```
cd backend
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini API key in `.env`:

```
GEMINI_API_KEY=your_api_key_here
```

Run backend:

```
uvicorn main:app --reload --port 8000
```

---

### 💻 Frontend Setup

```
cd frontend
npm install
npm run dev
```

Open in browser:

```
http://localhost:5173
```

---

## 🔑 Get Free Gemini API Key

1. Visit: https://aistudio.google.com/app/apikey  
2. Sign in with Google  
3. Click Create API Key  

Free tier includes:
- 15 requests/minute  
- 1M tokens/day  

---

## 📡 API Endpoints

### POST /api/chat
```
{
  "message": "Best biryani near campus",
  "history": []
}
```

### GET /api/restaurants
Query params:
- diet  
- budget_max  
- vibe  
- area  
- dish  

### GET /api/restaurant/{id}

### GET /api/health

---

## 🎨 UI Design

- Primary: #F97316  
- Secondary: #15803D  
- Background: #FFFBF5  
- Text: #1C1917  

Fonts:
- Inter  
- Playfair Display  

---

## ✅ Feature Checklist

- ✔ RAG chatbot with Gemini  
- ✔ Semantic + keyword search  
- ✔ Interactive map  
- ✔ Smart filters  
- ✔ Responsive UI  
- ✔ Chat history persistence  
- ✔ Typing indicator  
- ✔ Inline restaurant cards  

---

## 🚫 Constraints

- No paid APIs used  
- No Pinecone or cloud vector DB  
- No hardcoded frontend data  
- Fully local + free stack  

---

## 💡 Future Improvements

- Dark mode  
- "Open Now" status  
- Personalized recommendations  
- Voice-based search  

---

## 👨‍💻 Author

Built for students who know:
"Budget bhi chahiye aur taste bhi 😄"
