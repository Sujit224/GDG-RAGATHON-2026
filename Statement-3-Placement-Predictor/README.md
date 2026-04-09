# Placement Predictor & Mentor (Statement 3)

This module implements an end-to-end hiring-readiness workflow:

1. **Resume Parser (Bonus 1)**  
   Reads resume PDFs with PyPDF2 and extracts structured JSON fields:
   - CGPA
   - Tech Stack
   - Projects
   - Internships
   - Open Source Experience

2. **Regression Engine**  
   Trains a scikit-learn RandomForest pipeline on `data/placement_data.csv` and predicts a **0-100 Readiness Score** from parser output.

3. **Smart Experience Matcher (Bonus 2)**  
   Embeds candidate tech stack and performs cosine-similarity retrieval against a dummy vector DB of senior interview experiences, returning top 3 matches.

## Files

- `src/parser.py`: PDF-to-structured-JSON parser (LLM structured-output compatible).
- `src/predictor.py`: Model training + readiness score inference.
- `src/matcher.py`: Embedding-based top-3 mentor/interview experience matching.
- `data/placement_data.csv`: Dummy training data for readiness regression.

## Bonus Claims

✅ **Bonus 1 Claimed: Resume Parser**  
`parser.py` extracts required resume entities into structured JSON.

✅ **Bonus 2 Claimed: Smart Experience Matcher**  
`matcher.py` returns top 3 semantically similar senior interview experiences.

## Quick usage

```bash
python Statement-3-Placement-Predictor/src/predictor.py
python Statement-3-Placement-Predictor/src/matcher.py
```
