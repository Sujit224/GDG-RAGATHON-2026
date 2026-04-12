from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

db = FAISS.load_local("Statement-1-Insurance-Decoder/vectorstore/", embeddings, allow_dangerous_deserialization=True)

query = "extreme sports injury covered?"

docs = db.similarity_search(query, k=3)

for i, doc in enumerate(docs):
    print(f"\n--- Result {i+1} ---")
    print(doc.page_content[:300])