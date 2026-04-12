import streamlit as st
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings, ChatHuggingFace, HuggingFaceEndpoint
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

# --- 1. PAGE SETUP & CSS ---
st.set_page_config(page_title="IIITL Foodie Guide", page_icon="🍔", layout="centered")

# Custom CSS for a warm, "foodie" aesthetic
# st.markdown("""
# <style>
#     /* Gradient title */
#     h1 {
#         background: -webkit-linear-gradient(45deg, #FF6B6B, #FF8E53);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#         font-weight: 800;
#         text-align: center;
#     }
#     /* Subheader styling */
#     .subheader {
#         text-align: center;
#         color: #555555;
#         font-size: 1.1rem;
#         margin-bottom: 2rem;
#     }
#     /* Chat bubble styling for user */
#     [data-testid="stChatMessage"]:nth-child(odd) {
#         background-color: #FFF3E0; /* Warm orange tint */
#         border-radius: 15px;
#         padding: 10px;
#     }
#     /* Hide Streamlit branding */
#     #MainMenu {visibility: hidden;}
#     footer {visibility: hidden;}
#     header {visibility: hidden;}
# </style>
# """, unsafe_allow_html=True)
# Custom CSS for a warm, "foodie" aesthetic
st.markdown("""
<style>
    /* Gradient title */
    h1 {
        background: -webkit-linear-gradient(45deg, #FF6B6B, #FF8E53);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        text-align: center;
    }
    /* Subheader styling */
    .subheader {
        text-align: center;
        color: #888888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    /* Chat bubble styling for the assistant */
    [data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #FFF3E0; /* Warm orange tint */
        border-radius: 15px;
        padding: 10px;
    }
    /* THE FIX: Force the text inside the light bubble to be dark! */
    [data-testid="stChatMessage"]:nth-child(odd) p {
        color: #1E293B !important; 
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 2. CACHE THE HEAVY MODELS ---
# This ensures the LLM and DB only load once when the app starts, 
# preventing lag on every single chat message.
@st.cache_resource
def load_rag_system():
    load_dotenv()
    
    # Embeddings & Database
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma(
        persist_directory="Foodie_DB",
        embedding_function=embedding_model
    )
    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 6}
    )
    
    # LLM
    model = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.4,
        max_new_tokens=512
    )
    llm = ChatHuggingFace(llm=model)
    
    return retriever, llm

# Load the system
retriever, llm = load_rag_system()

# --- 3. PROMPT TEMPLATE ---
prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are the ultimate IIIT Lucknow Foodie Guide, a friendly and knowledgeable local expert helping students find the perfect place to eat.

Your objective is to recommend restaurants to the user based STRICTLY on the provided context.
While recommending places try to mention the values of the parameter on which the user 
wanted to do filtration (eg - if user says in budget, mention the budget of the place)

CRITICAL INSTRUCTIONS:
1. Grounded Recommendations: You will be provided with details of restaurants. Recommend ONLY from this list. Do not invent restaurants or prices.
2. Highlight the Best Parts: Use the 'Signature Dishes', 'Vibe', and 'Reviews' from the context to write a personalized, appetizing recommendation. Tell them WHY they should go there.
3. Empty Context Fallback: If the context is empty, it means no restaurants matched. Reply warmly: "I couldn't find any places matching those exact filters close by! Try expanding your search."
4. Tone: Keep it casual, energetic, and helpful—like a senior giving advice to a hungry junior after a long day of classes.

Context of matching restaurants:
{context}
"""
    ),
    (
        "human",
        """User's Request: {question}"""
    )
])

# --- 4. UI LAYOUT ---
st.title("🍔 The IIITL Foodie Guide 🍕")
st.markdown('<p class="subheader">Your ultimate senior guide to the best bites around campus and beyond.</p>', unsafe_allow_html=True)

# --- 5. CHAT HISTORY (SESSION STATE) ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hey there! Hungry after classes? Tell me what you're craving or your budget, and I'll find you the perfect spot! 🍜"}
    ]

# Display all previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 6. CHAT INPUT & RAG LOGIC ---
if user_query := st.chat_input("E.g., Suggest a budget-friendly Biryani place..."):
    
    # 1. Add user message to UI and history
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 2. Process the AI Response with a loading spinner
    with st.chat_message("assistant"):
        with st.spinner("Sniffing out the best spots... 🥘"):
            
            # Retrieve documents
            docs = retriever.invoke(user_query)
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Format prompt and invoke LLM
            final_prompt = prompt.invoke({
                "context": context,
                "question": user_query
            })
            
            response = llm.invoke(final_prompt)
            answer = response.content
            
            # Display answer
            st.markdown(answer)
            
    # 3. Save AI response to history
    st.session_state.messages.append({"role": "assistant", "content": answer})