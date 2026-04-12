import streamlit as st
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_groq import ChatGroq  # Replacement for ChatOpenAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Page Configuration
st.set_page_config(page_title="IIITL Food Scout", page_icon="🍜", layout="centered")
st.title("🍜 IIITL Food Scout")
st.caption("The ultimate RAG-powered food guide for IIIT Lucknow students.")

# 2. Environment & Paths
load_dotenv()
current_dir = os.path.dirname(os.path.abspath(__file__))
persist_directory = os.path.join(current_dir, "food_index_db")

# 3. Load the RAG System
@st.cache_resource
def init_food_scout():
    # Connect to your existing vector database
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_db = Chroma(
        collection_name="lucknow_foodie",
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
        
    
    # Initialize the LLM (Using 4o-mini for speed and cost)
    llm = ChatGroq(
        model="llama-3.3-70b-versatile", 
        temperature=0.7
    )
    
    # Define a Student-Centric Prompt
    system_prompt = (
        "You are the IIITL Food Scout, a helpful senior at IIIT Lucknow. "
        "Use the following pieces of retrieved context to recommend places to eat. "
        "If you don't know the answer, say you aren't sure, but suggest a general spot in Gomti Nagar. "
        "Be friendly and use student lingo like 'vibe', 'budget', and 'treat'."
        "\n\n"
        "{context}"
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create the modern chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(vector_db.as_retriever(), question_answer_chain)
    
    return rag_chain

# Initialize the chain
try:
    scout_chain = init_food_scout()
except Exception as e:
    st.error(f"Error loading the food database: {e}")
    st.stop()

# 4. Chat Session Management
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. User Interaction
if user_input := st.chat_input("Ask me about Biryani, Cafe vibes, or late-night spots..."):
    # Add user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("Scouting the best spots near Ahmamau..."):
            try:
                # Invoke the modern chain
                response = scout_chain.invoke({"input": user_input})
                full_response = response["answer"]
                
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Something went wrong: {e}")