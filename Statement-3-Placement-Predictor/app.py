import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from src.model_trainer import predict_readiness
from src.rag_pipeline import get_top_experiences
from src.llm_extractor import extract_profile_from_text, parse_pdf_resume

st.set_page_config(page_title="Placement Predictor & Mentor", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background-color: #050508;
        background-image: 
            radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.1) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.1) 0px, transparent 50%);
        color: #FAFAFA;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* Global Font Overrides */
    html, body, [class*="css"], .stMarkdown, .stText, .stChatFloatingInputContainer {
        font-family: 'Outfit', sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background-color: rgba(15, 17, 21, 0.8) !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 15px !important;
        margin-bottom: 1rem !important;
    }

    .score-dial {
        font-size: 72px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 20px;
        filter: drop-shadow(0 0 15px rgba(59, 130, 246, 0.3));
    }

    .stExpander {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
    }

    /* Button and Input Polish */
    .stButton>button {
        background: linear-gradient(135deg, #8b5cf6, #3b82f6) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 Placement Predictor & Mentor")
st.write("A hybrid GenAI and Regression system to score your readiness and match you with senior experiences!")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "extracted_profile" not in st.session_state:
    st.session_state.extracted_profile = None

# Context accumulator
all_context = ""

# Sidebar for Resume Upload
with st.sidebar:
    st.header("📄 Upload Resume (Bonus)")
    st.write("Extract details autonomously from your PDF resume.")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        with st.spinner("Parsing resume..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
                
            resume_text = parse_pdf_resume(tmp_path)
            os.remove(tmp_path)
            
            all_context += "\n--- RESUME DATA ---\n" + resume_text
            st.success("Resume parsed successfully!")
            
    st.divider()
    st.write("API Setting")
    api_key = st.text_input("Gemini API Key (optional if in .env)", type="password")
    if api_key:
        os.environ["GEMINI_API_KEY"] = api_key

# Main Layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("🗨️ Chat Profiling")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tell me about your CGPA, tech stack, and internships..."):
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
            
        with st.spinner("Analyzing profile..."):
            # Accumulate all history + new prompt + resume
            chat_context = "\n".join([m["content"] for m in st.session_state.chat_history])
            full_context = all_context + "\n--- CHAT DATA ---\n" + chat_context
            
            try:
                # Extract structured profile
                profile = extract_profile_from_text(full_context)
                st.session_state.extracted_profile = profile
                
                # Bot response logic
                bot_reply = profile.get("Missing_Info", "")
                if bot_reply and bot_reply.strip() != "":
                    final_reply = "I've updated your profile! " + bot_reply
                else:
                    final_reply = f"Great! Your profile looks solid. {profile.get('Summary', '')}"
                
                st.session_state.chat_history.append({"role": "assistant", "content": final_reply})
                with st.chat_message("assistant"):
                    st.markdown(final_reply)
                    
            except Exception as e:
                st.error(f"Error extracting profile: {e}")

with col2:
    st.subheader("📊 Readiness & Matching")
    
    if st.session_state.extracted_profile is not None:
        profile = st.session_state.extracted_profile
        
        # Dial
        try:
            score = predict_readiness(profile)
            st.markdown(f"<div class='score-dial'>{score:.1f} / 100</div>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #aaa'>Predicted Readiness Score</p>", unsafe_allow_html=True)
        except Exception as e:
            st.warning("Model needs to be trained first or there's an error.")
            st.code(e)
            
        st.divider()
        st.write("**Extracted Radar**")
        df_radar = {k: v for k, v in profile.items() if k not in ['Summary', 'Missing_Info']}
        st.dataframe(df_radar, use_container_width=True)
        
        st.divider()
        st.subheader("🧠 Top Matched Experiences")
        try:
            # Create a string representation for RAG matching
            profile_str = f"Tech Stack: {profile['Tech_Stack_Score']}, DSA: {profile['DSA_Skill']}, Projects: {profile['Project_Quality']}. Summary: {profile.get('Summary', '')}"
            experiences = get_top_experiences(profile_str)
            
            for exp in experiences:
                with st.expander(exp["title"]):
                    st.write(exp["content"])
        except Exception as e:
            st.warning("Index might be missing. Generating now...")
            # We could call index_experiences() here, but let's just show an error text
            st.error(str(e))
    else:
        st.info("Start chatting or upload a resume to see your predictions!")
