import streamlit as st
import os
import shutil
from decoder import get_insurance_answer
from vector_store import create_vector_db

# --- UI CONFIGURATION ---
st.set_page_config(page_title="Fine Print Decoder", page_icon="⚖️", layout="centered")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Load custom high-tech CSS
css_path = os.path.join(os.path.dirname(__file__), "style.css")
load_css(css_path)

st.title("⚖️ Fine Print Decoder")
st.markdown("### Simplify complex policy documents and hidden clauses.")

# --- SIDEBAR: FILE UPLOADER ---
with st.sidebar:
    st.header("📁 Document Management")
    uploaded_file = st.file_uploader("Upload a new Policy (PDF)", type="pdf")
    
    if uploaded_file is not None:
        # Save the file to the docs folder
        docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")
        os.makedirs(docs_dir, exist_ok=True)
        
        file_path = os.path.join(docs_dir, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"Uploaded: {uploaded_file.name}")
        
        # Trigger re-indexing
        if st.button("🔄 Re-index Database"):
            with st.spinner("AI is reading new documents..."):
                create_vector_db(docs_dir)
                st.rerun()

    st.divider()
    st.info("Primary Focus: Titan Secure Health Policy")
    st.markdown("""
    **Capabilities:**
    - 🔍 Clause Identification
    - 💡 ELI5 Simplification
    - 📖 Source Citations
    """)

# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT INPUT ---
if prompt := st.chat_input("Ask a question about your policy..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Decoding fine print..."):
            try:
                response = get_insurance_answer(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Error: {e}")