from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
import os
import json

# 🔑 Gemini setup
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# 🧠 Load DB
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

db = FAISS.load_local(
    "../vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = db.as_retriever(search_kwargs={"k": 3})


def ask(query, filter_type="all"):
    docs = retriever.invoke(query)

    context = "\n\n".join([
        f"[Page {d.metadata.get('page', '?')}]\n{d.page_content}"
        for d in docs
    ])

    filter_hint = {
        "coverage": "Focus on what IS covered.",
        "exclusions": "Focus on what is NOT covered.",
        "penalties": "Focus on penalties and fees.",
        "claims": "Focus on claims process.",
    }.get(filter_type, "")

    prompt = f"""
You are an expert insurance policy analyst.

STRICT RULES:
- ONLY use the provided context
- DO NOT hallucinate
- If not found, say "Not mentioned in policy"

{filter_hint}

Context:
{context}

Question:
{query}

Return STRICT JSON:
{{
  "direct_answer": "...",
  "eli5": "...",
  "citations": ["Section X", "Page Y"],
  "covered": true
}}
"""

    response = model.generate_content(prompt)
    text = response.text.strip()

    # Clean JSON (important)
    if text.startswith("```"):
        text = text.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(text)
    except:
        return {
            "direct_answer": "Parsing error",
            "eli5": "Something went wrong",
            "citations": [],
            "covered": None,
            "raw": text
        }