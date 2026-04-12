import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# Page Configuration
st.set_page_config(page_title="Insurance Decoder", page_icon="🛡️", layout="wide")

# Custom CSS for UI Enhancement
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
        scroll-behavior: smooth;
    }
    
    /* Hide top header and padding for a completely flush top */
    .stApp > header { display: none; }
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 1200px;
    }
    
    /* Premium Animated Dark Background */
    .stApp { 
        background: #050510;
        background-image: 
            radial-gradient(circle at 15% 50%, rgba(20, 250, 220, 0.08), transparent 25%),
            radial-gradient(circle at 85% 30%, rgba(65, 105, 225, 0.12), transparent 25%);
        color: #e2e8f0; 
    }
    
    /* Header styling with animated shimmer */
    h1 {
        background: linear-gradient(to right, #00f2fe, #4facfe, #00f2fe);
        background-size: 200% auto;
        color: #000;
        background-clip: text;
        text-fill-color: transparent;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 4s linear infinite;
        font-weight: 800;
        letter-spacing: -1px;
        margin-bottom: 0.5rem;
        font-size: 3.8rem !important;
        text-align: center;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.1);
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    /* Subtitle styling */
    .stMarkdown p {
        color: #94a3b8;
        font-size: 1.15rem;
        text-align: center;
    }
    
    /* Upload area styling center piece - glassmorphism */
    .stFileUploader {
        background: rgba(20, 250, 220, 0.03);
        border: 1px solid rgba(20, 250, 220, 0.2);
        border-radius: 24px;
        padding: 2.5rem;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(12px);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        margin-top: 1rem;
    }
    .stFileUploader:hover {
        background: rgba(20, 250, 220, 0.08);
        border-color: rgba(20, 250, 220, 0.6);
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(20, 250, 220, 0.15);
    }

    /* Chat message styling - Glass bubbles */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        margin-bottom: 1.5rem;
        padding: 1rem 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* User chat message - distinct tint */
    .stChatMessage[data-testid="stChatMessageUser"] {
        background: linear-gradient(135deg, rgba(0, 242, 254, 0.1) 0%, rgba(79, 172, 254, 0.05) 100%) !important;
        border-color: rgba(0, 242, 254, 0.3);
        margin-left: 2rem;
        border-bottom-right-radius: 4px;
    }
    
    /* Assistant chat message */
    .stChatMessage:not([data-testid="stChatMessageUser"]) {
        margin-right: 2rem;
        border-bottom-left-radius: 4px;
        border-left: 3px solid #4facfe;
    }

    /* Chat input styling */
    .stChatInputContainer {
        border-radius: 24px;
        background: rgba(15, 23, 42, 0.8) !important;
        border: 1px solid rgba(0, 242, 254, 0.3);
        box-shadow: 0 0 20px rgba(0,0,0,0.5);
        backdrop-filter: blur(20px);
    }
    .stChatInputContainer:focus-within {
        border-color: #00f2fe;
        box-shadow: 0 0 25px rgba(0, 242, 254, 0.2);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: rgba(5, 5, 16, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Insurance Decoder AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = None
# ----------------------------------------------------
st.markdown("<p style='font-size: 1.2rem; margin-top: -15px; margin-bottom: 30px; letter-spacing: 0.5px;'>Professional Document Analysis System</p>", unsafe_allow_html=True)

# Environment Setup
import warnings
import logging
load_dotenv()
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", message=".*Accessing.*__path__.*")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

# Resource Initialization
@st.cache_resource
def load_models():
    try:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        llm = ChatGroq(
            groq_api_key=os.getenv("GROQ_API_KEY"), 
            model_name="llama-3.1-8b-instant"
        )
        return embeddings, llm
    except Exception as e:
        st.error(f"Initialization Error: {e}")
        return None, None

embeddings, llm = load_models()

# Sidebar Components
st.sidebar.header("Document Center")
uploaded_file = st.sidebar.file_uploader("Upload Policy PDF", type="pdf")

if uploaded_file:
    # Handle File Upload
    with open("temp_policy.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Document Processing Pipeline
    if st.session_state.retriever is None:
        with st.spinner("Processing document..."):
            loader = PyPDFLoader("temp_policy.pdf")
            docs = loader.load()
            
            # Text Chunking
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = splitter.split_documents(docs)
            
            # Vector Store Creation
            vectorstore = FAISS.from_documents(splits, embeddings)
            st.session_state.retriever = vectorstore.as_retriever()
            st.session_state.doc_stats = {"pages": len(docs), "chunks": len(splits)}
            st.sidebar.success("Document Indexed Successfully")

    if "doc_stats" in st.session_state and st.session_state.doc_stats is not None:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📄 Document Info")
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Pages", st.session_state.doc_stats.get("pages", 0))
        col2.metric("Chunks", st.session_state.doc_stats.get("chunks", 0))
        
        # New Feature: Auto-Extract Key Details
        if st.sidebar.button("🪄 Auto-Extract Key Details", use_container_width=True):
            with st.spinner("Extracting hidden details..."):
                try:
                    summary_prompt = "Quickly scan the policy context and extract: 1. Insured Name (if any) 2. Policy Name/Type 3. Main Coverage Limit. Output as a bulleted markdown list."
                    # Get top 4 chunks as context to extract details
                    initial_context = "\n".join([doc.page_content for doc in st.session_state.retriever.get_relevant_documents("Policy holder coverage limit")][:4])
                    extraction = llm.invoke(f"Context: {initial_context}\n\n{summary_prompt}")
                    st.sidebar.info(extraction.content)
                except Exception as e:
                    st.sidebar.error("Could not extract details.")
                    
        st.sidebar.markdown("---")
    
    # Export Chat Feature
    if len(st.session_state.messages) > 0:
        chat_text = "\n\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages])
        st.sidebar.download_button("📥 Export Chat Log", data=chat_text, file_name="Insurance_Chat_Log.txt", mime="text/plain", use_container_width=True)

    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    # Chat Interface Initialization
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display Message History
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Suggested Questions (if no history yet)
    if len(st.session_state.messages) == 0:
        st.markdown("### Suggested Questions")
        cols = st.columns(3)
        suggestions = ["What are the exclusions?", "What is the deductible amount?", "Is there a waiting period?"]
        for i, suggestion in enumerate(suggestions):
            if cols[i].button(suggestion, use_container_width=True):
                # We can't perfectly mimic st.chat_input via button click without re-run tricks
                # So we just trigger a chat directly using session state.
                st.session_state.messages.append({"role": "user", "content": suggestion})
                st.rerun()

    # User Input Handling
    if query := st.chat_input("Ask a question about your policy:"):
        st.session_state.messages.append({"role": "user", "content": query})
        st.chat_message("user").write(query)

    # RAG Logic Implementation
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        user_query = st.session_state.messages[-1]["content"]
        
        # Build a brief conversation history string (last 4 messages)
        history_msgs = st.session_state.messages[-5:-1]
        history_str = "\n".join([f"{'Customer' if m['role']=='user' else 'AI'}: {m['content']}" for m in history_msgs])
        if not history_str:
            history_str = "No prior conversation."

        template = """You are a highly polite, professional, and friendly Insurance Advisory AI.
        Answer the customer's question thoroughly based only on the provided context.
        Always start with a warm opening and end with a polite closing.
        
        Context: {context}
        
        Recent Conversation History:
        {history}
        
        Customer's Question: {question}
        
        If the answer is not in the context, kindly and politely inform the customer that the specific information is unavailable in their document."""
        
        prompt = ChatPromptTemplate.from_template(template)
        
        def format_docs(docs):
            return "\n\n".join(doc.page_content for doc in docs)
        
        # Chain Definition
        if st.session_state.retriever is not None:
            chain = (
                {"context": st.session_state.retriever | format_docs, "history": lambda x: history_str, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
            )

            # Generate and Display Response
            with st.chat_message("assistant"):
                try:
                    # Add thinking animation
                    with st.spinner("🤖 Analyzing policy..."):
                        response = chain.invoke(user_query)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"Failed to generate response: {e}")
                    # Crucial Fix: Prevent soft-lock if API fails
                    st.session_state.messages.pop()
        else:
            with st.chat_message("assistant"):
                st.error("Please wait for the document to finish processing before asking questions.")
                st.session_state.messages.pop()

else:
    # Eye-pleasing Hero Section replacing the empty page
    st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem; background: rgba(56, 189, 248, 0.05); border-radius: 20px; border: 1px solid rgba(56, 189, 248, 0.2); margin-top: 2rem;">
            <h2 style="font-size: 2.5rem; font-weight: 800; margin-bottom: 1rem; background: linear-gradient(to right, #38bdf8, #818cf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Decode Your Policy in Seconds</h2>
            <p style="font-size: 1.2rem; color: #cbd5e1; max-width: 600px; margin: 0 auto 2rem auto;">Upload your insurance document and let our AI instantly summarize coverage, find hidden exclusions, and answer your complex queries in plain text.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><h3 style='text-align: center; color: #f8fafc;'>Why use Insurance Decoder?</h3><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 1.5rem; border-radius: 12px; height: 100%; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">⚡</div>
            <h4 style="color: #38bdf8;">Instant Answers</h4>
            <p style="color: #94a3b8; font-size: 0.95rem;">No more reading 50-page PDFs. Just ask "What is my deductible?" and get an instant, cited response.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 1.5rem; border-radius: 12px; height: 100%; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🛡️</div>
            <h4 style="color: #38bdf8;">Find Exclusions</h4>
            <p style="color: #94a3b8; font-size: 0.95rem;">Uncover hidden clauses and "Gotchas" before you make a claim. We highlight what's NOT covered.</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); padding: 1.5rem; border-radius: 12px; height: 100%; border: 1px solid rgba(255, 255, 255, 0.05);">
            <div style="font-size: 2rem; margin-bottom: 1rem;">🔒</div>
            <h4 style="color: #38bdf8;">Private & Secure</h4>
            <p style="color: #94a3b8; font-size: 0.95rem;">Your documents are processed locally in memory. We do not store your highly sensitive medical or vehicle data.</p>
        </div>
        """, unsafe_allow_html=True)