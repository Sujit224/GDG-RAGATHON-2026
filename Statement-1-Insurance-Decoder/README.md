# The Fine Print Decoder (Statement 1)

This module implements a high-stakes insurance RAG pipeline that reads a policy PDF, indexes it in ChromaDB, and retrieves the most relevant clauses for risk-sensitive user questions.

## What is implemented

- `src/main.py` contains the full retrieval pipeline using **LangChain + LlamaIndex + ChromaDB**.
- Policy ingestion from `docs/TITAN SECURE.pdf`.
- Embeddings via `sentence-transformers/all-MiniLM-L6-v2`.
- A high-stakes retriever configuration (`MMR`, broader fetch, diversified top-k).
- Strict system prompt forcing:
  - **ELI5 explanations**
  - **Exact Section + Clause citation in every answer**

## Source Attribution Bonus Claim

**Bonus Claimed: Source Attribution**

The prompt and retrieval formatting explicitly require and surface policy references with exact `Section` and `Clause` for each answer, satisfying source-attribution behavior for auditability and trust.

## Quick run

From repository root:

```bash
python Statement-1-Insurance-Decoder/src/main.py
```

This initializes the vector store, builds retrievers/indexes, and prints a prompt preview for a sample high-stakes insurance question.
