import streamlit as st
import os
from dotenv import load_dotenv
# Import the function we built earlier
from main import build_insurance_bot 

load_dotenv()

# --- Page Config ---
st.set_page_config(page_title="Fine Print Decoder", page_icon="📜")

st.title("📜 Fine Print Decoder")
st.subheader("Titan Secure Health Insurance Assistant")
st.markdown("Summarizing complex legal jargon into simple ELI5 terms with source attribution.")

# --- Sidebar ---
with st.sidebar:
    st.header("Project Info")
    st.info("Built for GDG RAGATHON 2026")
    if st.button("Clear Chat History"):
        st.session_state.messages = []

# --- Initialize RAG Bot ---
# We use @st.cache_resource so it only loads the PDF/Embeddings once!
@st.cache_resource
def load_bot():
    return build_insurance_bot()

try:
    qa_bot = load_bot()
except Exception as e:
    st.error(f"Error loading PDF: {e}")
    st.stop()

# --- Chat Interface ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Ask about coverage, exclusions, or penalties..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Decoding legal jargon..."):
            response = qa_bot.invoke(prompt)
            # RetrievalQA returns a dict, the answer is in 'result'
            answer = response["result"] 
            st.markdown(answer)
    
    # Add assistant message to history
    st.session_state.messages.append({"role": "assistant", "content": answer})