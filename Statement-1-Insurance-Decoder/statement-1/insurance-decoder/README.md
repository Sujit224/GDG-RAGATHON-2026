# Statement 1: Insurance Decoder 🛡️

## 📝 Problem Statement

Insurance policies are notoriously complex, filled with confusing legal jargon and clauses. Users struggle to understand what is covered, what is excluded, and under what conditions. This leads to unexpected out-of-pocket expenses and claim rejections. The "Insurance Decoder" aims to simplify the entire process, empowering users to make informed healthcare decisions.

## 💡 Solution

The Insurance Decoder is an AI-powered web platform that extracts information from your uploaded insurance document and simplifies it. By combining advanced Document Parsing (LangChain), Vector Embeddings (FAISS), and Large Language Models (OpenAI), the application provides a chat-based interface where users can ask questions directly and get clear, human-readable answers based *only* on their policy.

## ✨ Features

- **Interactive AI Chat:** Ask questions regarding coverage naturally (like ChatGPT).
- **PDF Upload:** Automatically load, chunk, and embed your insurance policy PDF.
- **Smart AI Summarization:** Answers are provided with simplified language based strictly on the uploaded document.
- **Instant Highlighting:** Clear visual tags (✅ Covered, ❌ Not Covered, ⚠️ Conditions) along with important keywords.
- **Risk Analyzer:** Evaluates custom healthcare scenarios and highlights potential risks or conditions.
- **Quick Questions:** Start immediately using predefined common questions.
- **Modern Clean UI:** A beautiful, responsive glassmorphism design with seamless interactions.

## 🛠️ Tech Stack

**Frontend**
- React 18
- Vite
- Axios
- CSS (Custom Glassmorphism Design)
- Lucide React (Icons)

**Backend**
- Python 3
- FastAPI (High performance API)
- LangChain Framework
- FAISS (Vector Database)
- OpenAI (Embeddings & LLM)

## 🚀 Setup Instructions

### Prerequisites
- Node.js (v18+)
- Python (v3.9+)
- OpenAI API Key

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create standard virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   - Rename `.env.example` to `.env`
   - Add your OpenAI API key to the `OPENAI_API_KEY` variable.
5. Run the FastAPI development server:
   ```bash
   uvicorn main:app --reload
   ```
   The backend will start at `http://localhost:8000`.

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The application will start, typically available at `http://localhost:5173`.

## 📸 Screenshots

*(Replace the placeholders below with actual your screenshots)*

- **Dashboard:**
  ![Dashboard Screenshot](#)
- **Asking a Question:**
  ![Chat Interaction](#)
- **Risk Analyzer:**
  ![Risk Analyzer Output](#)

## 🎥 Demo Video

Watch the complete solution walkthrough here: [Demo Video Link](https://youtube.com/your-demo-video-link)

---

*Built with ❤️ for GDG Ragathon 2026*
