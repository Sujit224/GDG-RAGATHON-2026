# 📜 RAGATHON 2026: Official Contribution Guidelines

> **Standards for Code Quality, Git Etiquette, and Team Collaboration.**

To ensure a fair and transparent evaluation, all teams must adhere to this workflow. Failure to follow these guidelines may result in point deductions during the final review.

---

## 1. Repository & Folder Integrity

Your work must be contained within the pre-defined directory structure. **Do not create new root-level folders.**

- **`/Statement-1-Insurance-Decoder`**: All RAG logic and UI for the Insurance challenge.
    
- **`/Statement-2-Lucknow-Foodie`**: Dataset, Hybrid Search, and UI for the Foodie Guide.
    
- **`/Statement-3-Placement-Predictor`**: LLM Extraction, Regression models, and RAG logic.
    
- **`/docs/official`**: Reference only. Do not modify files in this directory.
    

---

## 2. Team Workflow (The "3-Member" Rule)

**Collaboration is a core metric.** To qualify for evaluation, every registered team member must have visible commits in the repository history.

### ✅ Recommended Workflow:

1. **Fork & Clone:** One member forks the main repo; others clone that fork.
    
2. **Feature Branching:** Avoid working on the `main` branch. Create task-specific branches:
    
    - `git checkout -b feat/st1-rag-logic`
        
    - `git checkout -b feat/st3-regression-model`
        
3. **Atomic Commits:** Make small, frequent commits with clear, descriptive messages.
    
    - ❌ **Bad:** `git commit -m "fixed stuff"`
        
    - ✅ **Good:** `git commit -m "feat: implement PDF parser for resume upload bonus"`
        

---

## 3. Bonus & Creative Features

We track specific markers in your Git history to award bonus points.

- **Bonus Tags:** Use a dedicated commit message for bonus attempts (e.g., `bonus: added cosine similarity matcher`).
    
- **Documentation:** Every bonus attempted **must** be explicitly mentioned in the `README.md` of its respective folder.
    
- **Creative Edge:** If you add a feature not mentioned in the prompt (e.g., a Data Viz dashboard), document it under a `### Creative Features` heading in your folder's README.
    

---

## 4. Pull Request (PR) Requirements

Submit a **single Pull Request** from your fork to the main organization repository.

### 🏷️ PR Title Standard (Mandatory)

`[SUBMISSION] TeamName - Statements [X,Y,Z] + [BONUS: FeatureName]` _Example:_ `[SUBMISSION] Team-Alpha - Statements [1,3] + [BONUS: Resume-Parser, Smart-Matcher]`

### 📝 PR Description Template:

Your PR description must include:

- **Team Identity:** Team Name and Roll Numbers of all 3 members.
    
- **Challenges Completed:** List the Statements attempted.
    
- **Bonus Checklist:** Explicitly list which bonus features are functional.
    
- **Tech Stack:** List the LLMs (e.g., GPT-4o, Gemini), Vector DBs (e.g., ChromaDB), and Regression libraries (e.g., Scikit-learn) used.

### 🔗 The Final Link 
After hitting the PR, you must copy the **URL of your Pull Request** and paste it into the **Official Submission Google Form**. * **Deadline:** April 12th, 11:59 PM (Both PR and Form must be submitted).

> [!CAUTION] > **Submissions without a corresponding Google Form entry will not be evaluated.**
---

---

## 5. Folder-Level Documentation

Each problem statement folder must contain a `README.md` with:

1. **Setup Instructions:** How to run your code, including required Environment Variables (use a `.env.example`).
    
2. **System Architecture:** A brief explanation of your RAG pipeline (e.g., _Recursive Character Splitter -> OpenAI Embeddings -> FAISS_).
    
3. **Regression Metrics (Statement 3):** Mention the model used and the performance metric achieved (e.g., _Mean Squared Error_ or _R² Score_).
    

---

> [!WARNING] **Zero-Commit Policy:** Any team member with no contributions in the Git history will be marked as "Non-Participating," and the team's total score will be penalized.

**Happy Coding! 🚀** _GDG ML Wing, IIIT Lucknow_