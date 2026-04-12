import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

# --- 1. Page Configuration ---
st.set_page_config(page_title="TITAN SECURE Assistant", page_icon="🛡️", layout="centered")
# --- Custom CSS Styling ---
st.markdown("""
<style>
    /* Hide the default Streamlit top menu and footer for a cleaner app feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Style the main chat container to feel more like a messaging app */
    .stChatMessage {
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }

    /* Add a subtle glow to the user input box at the bottom */
    .stChatInput {
        border-radius: 20px !important;
        border: 1px solid #2563EB !important;
        box-shadow: 0 0 10px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Make the title stand out with a gradient */
    h1 {
        background: -webkit-linear-gradient(45deg, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. Cache the Heavy RAG Components ---
# @st.cache_resource ensures these models load exactly once when the app starts, 
# preventing lag on every new chat message.
@st.cache_resource
def load_rag_system():
    load_dotenv()

    # Load Embeddings & DB
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma(
        persist_directory="Chroma_DB",
        embedding_function=embedding_model
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 6,
            "fetch_k": 10,
            "lambda_mult": 0.5
        }
    )

    # Load LLM
    model = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.01,
        max_new_tokens=512
    )
    llm = ChatHuggingFace(llm=model)

    return retriever, llm

# Load the system in the background
retriever, llm = load_rag_system()

# --- 3. Define the Prompt Template ---
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a precise and strictly formatted AI assistant for the TITAN SECURE health insurance policy.
Your objective is to answer the user's question based ONLY on the provided context.

CRITICAL INSTRUCTION:
You MUST format your response exactly like the examples below. Do not use conversational filler (e.g., "Based on the text...", "Hello!"). Provide the direct outcome or answer, followed by a comma, and the exact section/point citation.

FORMAT EXAMPLES:
- No, per Section III, Point 2
- 40% penalty on the claim, per Section 2.2
- No, unless in Addendum B, which is not part of Platinum, per Section III, Point 4

If the answer is not contained within the provided context, you must reply exactly with:
"Information not found in the provided policy document."
"""
        ),
        (
            "human",
            """Context:
{context}

Question:
{question}
"""
        )
    ]
)

# --- 4. UI Layout & Styling ---
st.title("🛡️ TITAN SECURE Policy Assistant")
st.markdown("Ask me anything about your Tier-1 Individual Platinum health insurance policy.")

# --- 5. Session State for Chat History ---
# This keeps the conversation visible on the screen
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. Chat Input & Processing ---
if user_query := st.chat_input("E.g., What is the deductible?"):
    
    # Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # Show a loading spinner while the AI thinks
    with st.chat_message("assistant"):
        with st.spinner("Searching policy documents..."):
            
            # 1. Retrieve Documents
            docs = retriever.invoke(user_query)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # 2. Format the Prompt
            final_prompt = prompt_template.invoke({
                "context": context,
                "question": user_query
            })
            
            # 3. Get the Response
            response = llm.invoke(final_prompt)
            answer = response.content
            
            # Display the answer
            st.markdown(answer)
            
    # Add AI response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})