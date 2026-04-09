# 🎓 Statement 3: Placement Predictor & Mentor

> A hybrid AI system combining Generative AI profile extraction, Gradient Boosting regression, and ChromaDB RAG to predict student placement readiness and recommend senior interview experiences.

---

## 📖 Overview

The **Placement Predictor & Mentor** is a robust, multi-stage application designed for Statement 3 of the GDG RAGATHON. It allows students to supply their profile via an interactive AI Chat or a direct Resume Upload (Bonus feature). This data is then formatted into numeric parameters, passed through a highly-accurate Regression model, and ultimately queried against a Vector Database of 900+ senior interview experiences to display targeted insights.

---

## 🏗️ System Architecture

```
                 [ User Input ]
                 ↙             ↘
   (1) Chat Profiling       (2) Resume Upload
                 ↘             ↙
               [ Gemini 2.0 Flash ]
             (Structured JSON Extraction)
                        │
                        ▼
            [ 7 Profile Features ]
            (CGPA, DSA, Projects...)
            ↙                      ↘
[ GradientBoostingRegressor ]      [ ChromaDB Vector Search ]
       (R² = 0.91)                  (all-MiniLM-L6-v2)
            │                               │
            ▼                               ▼
    Readiness Score                 Top 3 Matched Senior
      (0-100)                      Interview Experiences
            ↘                               ↙
            [ Premium React Dashboard UI ]
```

---

## 📊 Regression Metrics

The prediction engine runs on a **Gradient Boosting Regressor** trained on the provided `normalized_placement_data.csv`.

- **Target:** `Readiness_Score` (0-100)
- **Features:** Academic_Score, DSA_Skill, Project_Quality, Experience_Score, OpenSource_Value, Soft_Skills, Tech_Stack_Score
- **Cross-Validation R² (5-Fold):** 0.9141 ± 0.0077
- **Test R² Score:** 0.9080
- **Mean Absolute Error (MAE):** 2.19

> Model artifacts (`readiness_model.pkl` and `scaler.pkl`) are saved in `src/model/` along with metrics evaluation.

---

## 🚀 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- **Google Gemini API Key** (Required for Chat & Resume parser)

### Quick Start

1. **Config Setup:**
   ```bash
   cp .env.example .env
   # Edit .env and paste your GOOGLE_API_KEY
   ```

2. **Backend (Terminal 1):**
   ```bash
   cd src
   pip install -r requirements.txt
   
   # Optional: Only run if you want to rebuild the vector db
   # python ingest_experiences.py  
   
   # Start the production API
   uvicorn app:app --port 8001 --reload
   ```

3. **Frontend (Terminal 2):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 📂 Project Structure
```
Statement-3-Placement-Predictor/
├── data/                       # CSVs, XLSX, and PDFs
├── src/                        # 🔙 Python Backend
│   ├── app.py                  # FastAPI Application (Ports 8001)
│   ├── ingest_experiences.py   # RAG pipeline populator
│   ├── train_model.py          # Regression model training loop
│   ├── model/                  # Serialized .pkl artifacts
│   └── chroma_db/              # Persistent Vector DB Collections
├── frontend/                   # ⚛️ React/Vite App
│   ├── src/components/         # Reusable premium glass UI bounds
│   └── ...
└── README.md
```

---

## ✨ Features & Bonus Implementations

### Core Requirements (70 Pts)
- ✅ **Chat-Based Profiling:** Utilizes Gemini to extract structured JSON points from human conversation seamlessly.
- ✅ **Regression Engine:** Custom-trained scikit-learn models offering excellent predictability logic (0-100).
- ✅ **Experience RAG:** Text parsing over unstructured CSV nodes + raw PDF embedding inside ChromaDB.

### Bonus Credits Active (+45 Pts)
- 🚀 **(Bonus 1) The Resume Parser (+15 Pts):** Integrated PyPDF and python-docx. Users can drop files into a specialized React dropzone which the API directly parses through few-shot LLM prompts to pull exact numeric features necessary for the model.
- 🚀 **(Bonus 2) Smart Experience Matcher (+30 Pts):** Executes deep semantic Cosine Sim searches in ChromaDB mapping the student's context summary instantly to the top relevant corporate interview narratives retrieved during ingestion.

### Creative Enhancements
- **Dynamic Score Visualization UI:** Built entirely custom CSS SVG gauge mechanisms that dynamically morph based on placement predictions.
- **Micro-Animations & Premium Design:** Implementing Glassmorphism techniques, complex box-shadows, and layout architectures identical strictly to high-value modern startups. Nothing looks standard-library!
