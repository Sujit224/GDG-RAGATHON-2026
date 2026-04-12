import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
import re

load_dotenv()

#  HELPER: Extract Section & Clause 


def extract_metadata(text: str, page: int):
    section_match = re.search(r"(SECTION [IVX]+|Section [IVX]+)", text, re.IGNORECASE)
    clause_match = re.search(r"(?:\b(\d+\.\d+|\d+)\b|\bPoint\s*(\d+)\b)", text, re.IGNORECASE)
    
    return {
        "section": section_match.group(1) if section_match else f"Page {page}",
        "clause": clause_match.group(1) or clause_match.group(2) if clause_match else "N/A",
        "page": page,
        "source": "TITAN SECURE.pdf"
    }

# LOAD MULTIPLE DOCUMENTS 


@st.cache_resource
def get_retriever():
  
    document_paths = [
        "docs/TITAN SECURE.pdf",
        
    ]
    
    all_docs = []
    for path in document_paths:
        if os.path.exists(path):
            loader = PyPDFLoader(path)
            raw_docs = loader.load()
            all_docs.extend(raw_docs)

    # Better Chunking

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=120,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    split_docs = text_splitter.split_documents(all_docs)

    for doc in split_docs:
        metadata = extract_metadata(doc.page_content, doc.metadata.get("page", 0))
        doc.metadata.update(metadata)

   
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")

    
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory="chroma_db_policy"
    )

    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 7, "fetch_k": 15}
    )

retriever = get_retriever()


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

#  PROMPT 


prompt = ChatPromptTemplate.from_template("""
You are the Titan Secure Fine Print Decoder Bot 🛡️

Answer using ONLY the provided context.
Explain in super simple ELI5 language (like to a 10-year-old).

Rules:
- ALWAYS start your answer with the exact Section and Clause/Page reference.
- Be friendly and clear.
- If not found in policy, say "This is not covered in the given policy."

Context:
{context}

Question: {question}

Answer:
""")

chain = prompt | llm



#  STREAMLIT UI 


st.set_page_config(page_title="Fine Print Decoder", page_icon="🛡️", layout="centered")
st.title("🛡️ Titan Secure Fine Print Decoder")
st.caption("RAG System • Multiple Documents • GDG-RAGATHON-2026")

st.markdown("**Ask anything** about coverage, exclusions, penalties, claims, etc.")


col1, col2, col3 = st.columns(3)
with col1:
    if st.button("Skydiving Injury?"):
        query = "Does this policy cover my bills if I get injured while Skydiving?"
with col2:
    if st.button("MRI Penalty?"):
        query = "What happens if I forget to get a pre-authorization for an MRI?"
with col3:
    if st.button("Homeopathy?"):
        query = "Is Homeopathy covered in the Platinum tier?"

query = st.text_input("Type your question here:", placeholder="What is the deductible? Do they cover pre-existing conditions?")

if query:
    with st.spinner("Analyzing policy documents..."):
        docs = retriever.invoke(query)
        
        context_str = "\n\n".join([
            f"**Section: {d.metadata.get('section')} | Clause: {d.metadata.get('clause')} | Page: {d.metadata.get('page')}**\n{d.page_content.strip()}"
            for d in docs
        ])
        
        response = chain.invoke({"context": context_str, "question": query})
        
        st.success("✅ Answer Ready!")
        st.write(response.content)
        
        with st.expander("📌 Sources Used (For Transparency)"):
            for d in docs:
                st.write(f"**Section {d.metadata.get('section')}**, Clause {d.metadata.get('clause')}, Page {d.metadata.get('page')}")
                st.caption(d.page_content[:300] + "...")