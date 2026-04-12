from src.rag.retriever import get_interviews

dummy_profile = {
    "skills": ["DSA", "Python"]
}

results = get_interviews(dummy_profile)

for i, r in enumerate(results):
    print(f"\n--- Result {i+1} ---\n")
    print(r[:300])