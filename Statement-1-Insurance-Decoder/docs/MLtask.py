from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from sentence_transformers import SentenceTransformer

loader = PyPDFLoader("Titan_Secure_Health_Insurance.pdf")
documents = loader.load()


splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150
)
chunks = splitter.split_documents(documents)


for chunk in chunks:
    chunk.metadata["source"] = f"Page {chunk.metadata.get('page', 'N/A')}"


model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [c.page_content for c in chunks]
vectors = model.encode(texts)

vectorstore = FAISS.from_embeddings(
    list(zip(texts, vectors)),
    embedding=model
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 5})


def classify_query(query):
    q = query.lower()
    if "cover" in q:
        return "coverage"
    elif "penalty" in q:
        return "penalty"
    elif "exclude" in q or "not covered" in q:
        return "exclusion"
    return "general"


llm = ChatOpenAI(model="gpt-4o-mini")


prompt = PromptTemplate(
    template="""
You are a strict insurance analyst.

Rules:
- ONLY answer using the provided context
- If exact answer is NOT explicitly stated, say: "Not mentioned in the policy"
- DO NOT guess or assume

Output format:

Answer:
<clear answer>

Source:
<page number>

ELI5:
<simple explanation>

Question: {question}
Context: {context}
""",
    input_variables=["question", "context"]
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    chain_type_kwargs={"prompt": prompt},
    return_source_documents=True
)


query = "Does this policy cover injuries from extreme sports?"

query_type = classify_query(query)

if query_type == "exclusion":
    retriever.search_kwargs = {"k": 10}
elif query_type == "coverage":
    retriever.search_kwargs = {"k": 6}
else:
    retriever.search_kwargs = {"k": 5}


result = qa_chain({"query": query})

print(result["result"])

for doc in result["source_documents"]:
    print(f"{doc.metadata.get('source', 'Unknown')}")
    print(doc.page_content[:300])
    print("-" * 50)