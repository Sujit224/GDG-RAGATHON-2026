# 🚀 Placement Readiness Predictor

A Streamlit-based web application that predicts a student's placement readiness score using either **resume input** or **manual profile data**.

---

## 📌 Features

* 📄 **Resume Analysis** – Paste your resume and get structured insights
* 🧠 **Smart Scoring System** – Rule-based scoring for realistic evaluation
* 🖥️ **Interactive UI** – Built with Streamlit (runs in browser)
* ✍️ **Manual Input Mode** – Enter CGPA, projects, skills, etc.
* 💡 **Actionable Feedback** – Get suggestions to improve your profile

---

## 🧠 How It Works

The system follows a simple pipeline:

```
Resume / User Input → Data Extraction → Feature Mapping → Scoring → Result
```

### 📊 Scoring Breakdown (Out of 100)

| Factor      | Max Score |
| ----------- | --------- |
| CGPA        | 20        |
| Projects    | 20        |
| Internships | 20        |
| Skills      | 20        |
| DSA Level   | 20        |

---

## 🛠️ Tech Stack

* Python 🐍
* Streamlit 🌐
* Regex (for resume parsing)
* Scikit-learn (optional ML support)

---

## 📂 Project Structure

```
Statement-3-Placement-Predictor/
│
├── data/
├── src/
│   ├── app.py              # Streamlit UI
│   ├── extractor.py       # Resume text processing
│   ├── rag_engine.py      # Scoring logic
│   ├── regressor.py       # ML model (optional)
│   ├── chatbot.py
│   ├── embeddings.py
│   ├── resume_parser.py
│   ├── train.py           # Model training script
│   └── model.pkl          # Saved model (ignored in git)
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ▶️ Getting Started

### 1️⃣ Clone the Repository

```
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Run the App

```
streamlit run src/app.py
```

---

## 📥 Input Options

### ✅ Option 1: Resume Input

* Paste your resume text
* App extracts:

  * CGPA
  * Skills
  * Projects
  * Internships
  * DSA level (estimated)

### ✅ Option 2: Manual Input

* Enter details using sliders and inputs

---

## 📈 Example

**Input:**

* CGPA: 7.0
* Projects: 1
* Internships: 0
* Skills: 3
* DSA: 5

**Output:**

```
Readiness Score: 34/100
```

---

## 💡 Suggestions Engine

The app provides feedback like:

* Build more projects
* Gain internship experience
* Improve DSA skills

---

## 🚫 .gitignore Recommendations

```
venv/
.env
__pycache__/
*.pkl
```









