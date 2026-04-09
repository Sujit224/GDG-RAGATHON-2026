# 🚀 Placement Predictor & Mentor AI

An **AI-powered hybrid system** that predicts a student's placement readiness score and provides personalized guidance using **Machine Learning + Generative AI + Resume Parsing + Smart Matching**.

---

## 🧠 Overview

Placement preparation is often **unstructured and confusing**.
This project solves that by combining:

* 📊 **Regression-based Prediction**
* 🤖 **LLM-powered Profile Extraction**
* 📄 **Resume Parsing (PDF/DOCX)**
* 🔍 **Smart Experience Matching (Cosine Similarity)**

👉 Result: A **complete placement mentor system**.

---

## ⚡ Features

### 🎯 1. Chat-Based Profiling

* Interactive chatbot collects:

  * CGPA
  * Tech Stack
  * Projects
  * Internships
  * Communication skills
  * Open source contributions

---

### 📄 2. Resume Parser (Bonus ⭐)

* Upload **PDF/DOCX resume**
* Automatically extracts:

  * CGPA
  * Skills
  * Experience
  * Projects

---

### 🧾 3. Structured JSON Extraction

* LLM converts raw input → clean JSON

```json
{
  "cgpa": 8.5,
  "projects": 3,
  "internships": 1,
  "communication": 7,
  "open_source": 1,
  "tech_stack": ["React", "Node", "AWS"]
}
```

---

### 📊 4. Placement Prediction Engine

Hybrid model combining:

* ✅ Regression logic
* ✅ Real-world placement rules

👉 Outputs:

* Readiness Score (0–100)
* Placement Level (Low / Medium / High)

---

### 🧑‍🏫 5. AI Mentor Feedback

* Strengths
* Weaknesses
* Actionable roadmap

---

### 🔍 6. Smart Experience Matcher (Bonus ⭐⭐)

* Uses **TF-IDF + Cosine Similarity**
* Matches student profile with interview datasets

👉 Returns:

* Top 3 relevant companies
* Interview insights
* Why it matches

---

### 📈 7. Explainable AI

Every prediction includes:

* Reasoning
* Feature impact
* Suggestions

---

## 🏗️ Architecture

```
Frontend (React Chat UI)
        ↓
FastAPI Backend
 ├── Resume Parser (PDF/DOCX)
 ├── LLM (JSON Extraction)
 ├── Prediction Engine (Hybrid Model)
 ├── Experience Matcher (Cosine Similarity)
 └── Response Generator
```

---

## 🛠️ Tech Stack

### 🔹 Frontend

* React
* Tailwind CSS

### 🔹 Backend

* FastAPI
* Python

### 🔹 AI/ML

* Scikit-learn
* TF-IDF Vectorizer
* Cosine Similarity

### 🔹 Resume Parsing

* pdfplumber
* python-docx

---

## 🚀 API Endpoints

### 📤 Upload Resume

```
POST /upload_resume
```

---

### 🧠 Extract Profile

```
POST /extract
```

---

### 📊 Predict Score

```
POST /predict
```

---

### 🔍 Match Experiences

```
POST /match
```

---

### ⚡ Full Pipeline

```
POST /analyze_resume
```

👉 Returns:

* Profile
* Score
* Recommendations

---

## 📊 Scoring Logic (Hybrid)

### ML-Based:

```
score =
  (cgpa * 6) +
  (projects * 3) +
  (internships * 8) +
  (communication * 4)
```

### Rule-Based Adjustments:

* CGPA ≥ 9 → boost
* Internships ≥ 2 → strong boost
* No internships → penalty
* Low communication → penalty

---

## 🔍 Experience Matching Logic

1. Convert skills → vectors (TF-IDF)
2. Compare with dataset
3. Apply cosine similarity
4. Return top 3 matches

---

## 🧪 Example Output

```json
{
  "score": 82,
  "level": "High",
  "reasons": [
    "Strong CGPA boosted score",
    "Internship improved readiness"
  ],
  "recommended_experiences": [
    {
      "company": "Amazon",
      "match_score": 0.89,
      "summary": "DSA + system design"
    }
  ]
}
```

---

## ⚙️ Installation

```bash
# Clone repo
git clone <repo-url>

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
```

---

## 📦 Requirements

```
fastapi
uvicorn
pdfplumber
python-docx
scikit-learn
```

---

## 🏆 Why This Project Stands Out

✅ Hybrid AI system (ML + Rules + LLM)
✅ Real-world placement logic
✅ Resume automation (no manual input)
✅ Personalized recommendations
✅ Explainable predictions

---

## 🔮 Future Improvements

* Resume ATS scoring
* Real dataset training
* Dashboard with charts
* Company-wise preparation roadmap

---

## 👨‍💻 Author

Built for hackathon excellence 🚀

---

## 💡 Pitch Line (Use This!)

> “This is not just a predictor — it’s an AI-powered placement mentor combining resume intelligence, predictive modeling, and personalized recommendations.”

---

## ⭐ If you like this project

Give it a ⭐ and share!
