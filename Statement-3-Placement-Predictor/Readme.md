# 🚀 PlaceIQ — AI Placement Predictor & Mentor

PlaceIQ is an intelligent full-stack AI system that helps students evaluate their **placement readiness** and provides **personalized guidance** using a combination of:

* 🤖 Generative AI (LLM-based conversational profiling)
* 📊 Machine Learning (Regression model for scoring)
* 📚 RAG (Retrieval-Augmented Generation for interview experiences)

---

## 🎯 Problem Statement

Students often struggle to understand:

* How ready they are for placements
* What skills they lack
* What real interview experiences look like

**PlaceIQ solves this by combining AI + ML + real-world data into one system.**

---

## 🧠 Key Features

### 💬 AI Chat Mentor

* Conversational AI gathers student profile
* Friendly, step-by-step questioning
* Extracts structured data automatically

### 📊 Placement Readiness Score

* ML regression model predicts score (0–100)
* Based on:

  * CGPA
  * Projects
  * Internships
  * Communication skills
  * Open source contributions
  * Tech stack strength

### 📚 RAG Interview Insights

* Fetches relevant senior interview experiences
* Uses FAISS + embeddings for semantic search
* Helps students learn from real examples

### 📈 Interactive Dashboard

* Profile visualization
* Animated score gauge
* Interview experience cards

---

## 🏗️ Tech Stack

| Layer       | Technology                      |
| ----------- | ------------------------------- |
| Frontend    | React + Vite + TailwindCSS      |
| Backend     | FastAPI                         |
| ML Model    | scikit-learn (Ridge Regression) |
| Vector DB   | FAISS                           |
| Embeddings  | sentence-transformers           |
| LLM         | Anthropic Claude API            |
| PDF Parsing | PyMuPDF                         |

---

## 📁 Project Structure

```
placeiq/
├── backend/
│   ├── main.py
│   ├── routers/
│   ├── services/
│   ├── models/
│   ├── data/
│   └── requirements.txt
│
└── frontend/
    ├── src/
    ├── components/
    ├── hooks/
    └── package.json
```

---

## ⚙️ How It Works

1. 🧑 Student interacts with AI chat
2. 🤖 AI collects profile data
3. 📊 ML model predicts readiness score
4. 📚 RAG retrieves relevant interview experiences
5. 📈 Results shown in dashboard

---

## 🔄 System Flow

```
User Input → AI Chat → Profile Extraction
           → ML Model → Score Prediction
           → RAG → Interview Retrieval
           → UI Dashboard
```

---

## 🛠️ Setup Instructions

### 🔹 Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

---

### 🔹 Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## 🔑 Environment Variables

Create a `.env` file in backend:

```
ANTHROPIC_API_KEY=your_api_key_here
```

⚠️ Do NOT push `.env` to GitHub.

---

## 📊 ML Model Details

* Algorithm: Ridge Regression
* Output: Placement readiness score (0–100)
* Features:

  * CGPA
  * Projects
  * Internships
  * Communication
  * Open Source
  * Tech Stack Score

---

## 📚 RAG System

* Uses FAISS vector database
* Embeddings: sentence-transformers
* Data Source: Interview experience PDF
* Retrieves top relevant experiences

---

## 🚀 Future Improvements

* 🔍 Better PDF parsing using NLP
* 📈 Advanced ML models (XGBoost, Neural Nets)
* 🧠 Personalized roadmap generation
* 🌐 Deployment (Docker + Cloud)

---

## 👨‍💻 Author

**Team CtrlX**
Hackathon Project 🚀

---

## ⭐ Contribute

Feel free to fork, improve, and raise PRs!

---

## 📌 Note

This project was built as part of a hackathon and demonstrates integration of:

* AI + ML + RAG in a real-world use case


---

## ❤️ If you like this project

Give it a ⭐ on GitHub!
