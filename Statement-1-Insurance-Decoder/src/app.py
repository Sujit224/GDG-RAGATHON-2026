import streamlit as st
import os

# Ensure the UI works even if API key is not instantly available, we give a warning.
from dotenv import load_dotenv
load_dotenv()

from rag_chain import get_rag_chain

st.set_page_config(page_title="Titan Secure Health - Policy Decoder", page_icon="📝", layout="centered")

st.markdown("""
# 📝 Titan Secure Health - Policy Decoder
Welcome to the Fine Print Decoder! This bot uses a high-precision Retrieval-Augmented Generation (RAG) system to simplify the complex terms and conditions in your health insurance policy.

Ask questions about **coverage**, **penalties**, or **exclusions**, and get simple explanations backed by precise Section and Clause identifiers.
""")

# Setup sidebar to allow user to add API key if missing
with st.sidebar:
    st.header("Settings")
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        st.warning("Groq API Key is missing!")
        api_key_input = st.text_input("Enter your Groq API Key:", type="password")
        if api_key_input:
            os.environ["GROQ_API_KEY"] = api_key_input
            st.success("API Key loaded temporarily! Now you can run ingest.py to parse your PDF or chat if DB is prepared.")
    else:
        st.success("Groq API Key is configured.")
        
    st.markdown("### Powered by:")
    st.markdown("- **Langchain** & **Groq** (llama-3.3-70b-versatile)")
    st.markdown("- **ChromaDB** for Vector Search")
    st.markdown("- **PyMuPDF** for Document Parsing")
    st.markdown("---")
    st.markdown("### Database Notice")
    st.markdown("Please make sure you have run `python src/ingest.py` to index your PDF before chatting.")

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you decode your insurance policy today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("E.g., Does this policy cover injuries from extreme sports?"):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # check API Key
    if not os.getenv("GROQ_API_KEY") or os.getenv("GROQ_API_KEY") == "your_groq_api_key_here":
        error_msg = "🚨 Provide a Groq API Key in the sidebar or `.env` file before querying."
        st.chat_message("assistant").write(error_msg)
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        st.stop()

    try:
        with st.chat_message("assistant"):
            with st.spinner("Decoding Policy..."):
                rag_chain = get_rag_chain()
                response = rag_chain.invoke(prompt)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
    except FileNotFoundError:
         error_msg = "🚨 Vector database not found. Please run `python ingest.py` in the `src` folder first to index the PDF document."
         st.error(error_msg)
         st.session_state.messages.append({"role": "assistant", "content": error_msg})
    except Exception as e:
        st.error(f"Error fetching response: {e}")
