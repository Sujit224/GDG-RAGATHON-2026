# 🧠 Insurance Decoder AI (Statement 1)

An AI-powered web application that simplifies complex insurance policy documents into clear, user-friendly answers using a Retrieval-Augmented Generation (RAG) pipeline.

---

## 🚀 Problem Statement

Insurance policies are often lengthy, complex, and filled with legal jargon, making it difficult for users to understand coverage, exclusions, and conditions.

---

## 💡 Solution

Insurance Decoder AI allows users to:

* Upload insurance policy PDFs
* Ask natural language questions
* Get simple, accurate answers based on the document

---

## ✨ Features

* 📄 Upload insurance policy PDF
* 💬 Chat-based question answering
* 🧠 Context-aware responses using RAG
* ⚡ Fast inference using Groq LLM
* 🆓 Free embeddings using HuggingFace
* 🎯 Highlights:

  * ✅ Covered
  * ❌ Not Covered
  * ⚠️ Conditions

---

## 🏗️ Tech Stack

### Frontend

* React (Vite)
* Axios
* Modern UI

### Backend

* FastAPI
* LangChain
* FAISS (Vector Database)

### AI/ML

* Groq (LLM)
* HuggingFace Embeddings (`all-MiniLM-L6-v2`)

---

## ⚙️ Project Structure

```
statement-1/
└── insurance-decoder/
    ├── frontend/
    │   ├── src/
    │   ├── package.json
    │
    ├── backend/
    │   ├── main.py
    │   ├── requirements.txt
    │   └── .env (not committed)
    │
    ├── README.md
```

---

## 🔑 Environment Variables

Create a `.env` file inside `backend/`:

```
GROQ_API_KEY=your_groq_api_key_here
```

⚠️ Do NOT commit `.env` to GitHub.

---

## 🛠️ Installation & Setup

### 1️⃣ Clone Repository

```
git clone https://github.com/your-username/repo-name.git
cd statement-1/insurance-decoder
```

---

### 2️⃣ Backend Setup

```
cd backend
python3 -m venv venv
source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

Run backend:

```
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 3️⃣ Frontend Setup

```
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

---

## 🧪 Example Queries

* Is MRI covered?
* What is deductible?
* Is skydiving covered?
* What happens without approval?

---

## 🧠 How It Works

1. User uploads PDF
2. Text is extracted and split
3. Converted into embeddings (HuggingFace)
4. Stored in FAISS vector DB
5. Query retrieves relevant context
6. Groq LLM generates final answer

---

## 🎥 Demo

(Add your demo video link here)

---

## 🚀 Future Improvements

* Multiple document comparison
* Risk analysis feature
* Policy recommendation system
* Better UI/UX

---

## 📜 License

This project is for educational and hackathon purposes.
