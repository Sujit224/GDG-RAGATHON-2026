import os
import warnings
import logging

# Suppress warnings and verbose logs from HuggingFace, sentence-transformers, and Sklearn
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
warnings.filterwarnings("ignore")
warnings.filterwarnings("ignore", message=".*Accessing.*__path__.*")
logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("sentence_transformers").setLevel(logging.ERROR)
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)

import pickle
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
# --- 1. SETUP ---
load_dotenv(os.path.join(os.getcwd(), '.env'), override=True)
api_key = os.getenv("GROQ_API_KEY")

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

# Resources Loading
@st.cache_resource
def load_all():
    # ML Model load karna critical hai
    with open('placement_model.pkl', 'rb') as f:
        model = pickle.load(f)
    
    retriever = None
    if os.path.exists("INTERVIEW_EXPERIENCES.pdf"):
        try:
            embeddings = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            loader = PyPDFLoader("INTERVIEW_EXPERIENCES.pdf")
            docs = loader.load()
            vectorstore = FAISS.from_documents(docs, embeddings)
            retriever = vectorstore.as_retriever()
        except Exception as e:
            st.sidebar.warning("⚠️ RAG Offline: Using LLM only (No PDF Context)")
            retriever = None
            
    return model, retriever

ml_model, retriever = load_all()
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=api_key)

# --- 2. UI ---
st.set_page_config(page_title="Placement Predictor", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Vibrant Aurora Glassmorphism */
    .stApp { 
        background: linear-gradient(135deg, #1A0B2E, #091236, #300C35, #0B192C);
        background-size: 300% 300%;
        animation: auroraBG 16s ease infinite;
        color: #ffffff !important;
    }
    
    @keyframes auroraBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    h1 {
        font-size: 4rem !important;
        font-weight: 900 !important;
        text-align: center;
        background: linear-gradient(to right, #00F2FE, #4FACFE, #FF0844, #FFB199);
        background-size: 300% auto;
        color: #fff;
        background-clip: text;
        text-fill-color: transparent;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 5s linear infinite;
        text-shadow: 0 0 20px rgba(0, 242, 254, 0.2);
    }
    
    @keyframes shine {
        to { background-position: 300% center; }
    }
    
    h2, h3, p, label, .stMarkdownContainer p {
        color: #ffffff !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Neon Glow Upload Area */
    .stFileUploader {
        background: rgba(255, 255, 255, 0.05);
        border: 2px dashed #00F2FE;
        border-radius: 20px;
        padding: 2.5rem;
        transition: all 0.4s ease;
        backdrop-filter: blur(12px);
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.1);
    }
    .stFileUploader:hover {
        background: rgba(0, 242, 254, 0.1);
        border-color: #FF0844;
        transform: translateY(-5px);
        box-shadow: 0 10px 40px rgba(255, 8, 68, 0.3);
    }
    
    /* Modern Pill Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        justify-content: center;
        background: rgba(255,255,255,0.05);
        padding: 12px;
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 50px !important;
        padding: 8px 30px;
        font-size: 1.15rem;
        font-weight: 800;
        color: #A0AEC0;
        border: none;
        transition: all 0.3s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF0844 0%, #FFB199 100%);
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(255, 8, 68, 0.4);
        border: none !important;
    }
    
    /* Futuristic Buttons */
    .stButton > button {
        background: rgba(255,255,255,0.05);
        color: #00F2FE !important;
        font-weight: 800;
        border: 2px solid #00F2FE;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        box-shadow: 0 0 15px rgba(0, 242, 254, 0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(to right, #00F2FE, #4FACFE);
        color: #ffffff !important;
        border-color: transparent;
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 242, 254, 0.5);
    }
    
    /* General Fixes */
    .stAlert p { color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

st.write("<h1 style='text-align: center; width: 100%;'>🎓 Smart Placement Predictor</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 1.2rem; font-weight: 600; margin-bottom: 2rem;'>Unlock Your Career Potential with AI</p>", unsafe_allow_html=True)

# Main Hero Layout for Upload
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("### Step 1: Upload Your Resume")
    uploaded_resume = st.file_uploader("Upload YOUR Resume (PDF)", type="pdf", label_visibility="collapsed")

if uploaded_resume:
    file_bytes = uploaded_resume.getbuffer()
    file_id = uploaded_resume.size
    
    if "current_file_id" not in st.session_state or st.session_state.current_file_id != file_id:
        st.session_state.current_file_id = file_id
        
        with open("temp_user_resume.pdf", "wb") as f:
            f.write(file_bytes)
        
        with st.spinner("AI is analyzing your Resume... This only happens once!"):
            try:
                # A. Extract Data
                res_loader = PyPDFLoader("temp_user_resume.pdf")
                res_text = " ".join([p.page_content for p in res_loader.load()])[:4000]
                
                prompt = ChatPromptTemplate.from_template(
                    "Read this Resume: {text}\nExtract scores (0-10) for: Academic_Score, DSA_Skill, "
                    "Project_Quality, Experience_Score, OpenSource_Value, Soft_Skills, Tech_Stack_Score. "
                    "Return ONLY JSON."
                )
                chain = prompt | llm | JsonOutputParser()
                data = chain.invoke({"text": res_text})
    
                # B. Clean & Predict
                feats = ['Academic_Score', 'DSA_Skill', 'Project_Quality', 'Experience_Score', 
                         'OpenSource_Value', 'Soft_Skills', 'Tech_Stack_Score']
                cleaned = {f: float(data.get(f, 0)) if not isinstance(data.get(f, 0), dict) else 0.0 for f in feats}
                
                prediction = ml_model.predict(pd.DataFrame([cleaned])[feats])
    
                # C. Advice and Target Companies
                advice = "Keep working on your projects!"
                if retriever:
                    ctx = retriever.invoke(f"Advice for DSA {cleaned['DSA_Skill']}")
                    docs_text = "\n".join([doc.page_content for doc in ctx[:2]])
                    advice = llm.invoke(f"Context: {docs_text}\n\nBased on these scores ({cleaned}), provide an encouraging career action plan and explicitly list 3-5 realistic target companies they should apply to.").content
                else:
                    advice = llm.invoke(f"Based on these scores ({cleaned}), provide an encouraging career action plan and explicitly list 3-5 realistic target companies they should apply to.").content
                    
                match_prompt = f"Based on these resume scores: {cleaned}. Generate 3 highly specific realistic Job Opportunities for them. Format as a markdown list: '1. **Job Title** at **Company**: Brief why they fit and expected salary range.' Do not add extra text."
                matches = llm.invoke(match_prompt).content
                
                st.session_state.cleaned = cleaned
                st.session_state.prediction = prediction
                st.session_state.advice = advice
                st.session_state.matches = matches
                st.session_state.feats = feats
                st.session_state.ai_err = None
            except Exception as e:
                st.session_state.ai_err = str(e)

    if st.session_state.get("ai_err"):
        st.error(f"Error AI Processing: {st.session_state.ai_err}")
    else:
        cleaned = st.session_state.cleaned
        prediction = st.session_state.prediction
        advice = st.session_state.advice
        matches = st.session_state.matches
        feats = st.session_state.feats

        # --- 3. DISPLAY & TABS ---
        st.markdown("---")
        tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🎛️ What-If Simulator", "💼 Career & Job Matches"])
        
        with tab1:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                st.subheader("📊 Your AI Analyzed Profile")
                plot_data = pd.DataFrame({"Score": list(cleaned.values())}, index=list(cleaned.keys()))
                st.area_chart(plot_data, width='stretch')
                
                # NEW FUNCTIONALITY: Skill Gap Insight
                lowest_skill = min(cleaned, key=cleaned.get)
                st.info(f"💡 **AI Insight:** Your lowest area is **{lowest_skill.replace('_', ' ')}** ({cleaned[lowest_skill]}/10). Focus heavily on improving this area first to maximize your chances!")
                
                if prediction[0] == 1: 
                    st.success("### 🎉 LIKELY PLACED\nYour profile is extremely competitive!")
                else: 
                    st.warning("### ⚠️ NEEDS IMPROVEMENT\nFollow the action plan to boost your metrics.")
                    
            with col2:
                st.subheader("🚀 Personalized Action Plan")
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.05); border-left: 4px solid #00F2FE; padding: 1.5rem; border-radius: 12px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(0,0,0,0.2);">
                    {advice}
                </div>
                """, unsafe_allow_html=True)
                
                # Enhanced Export functionality
                st.markdown("<br>", unsafe_allow_html=True)
                export_text = f"Placement Analysis Report\n\nPrediction: {'Placed' if prediction[0]==1 else 'Not Placed'}\n\nScores:\n{cleaned}\n\nAction Plan:\n{advice}"
                st.download_button("📥 Download Full Career Report", data=export_text, file_name="Career_Report.txt", mime="text/plain", width=True)
        
        with tab2:
            st.subheader("🎛️ What-If Simulator")
            st.markdown("Play around with your metrics! Drag the sliders to see what specific skills you need to push up to alter your placement prediction.")
            
            with st.form("what_if_form"):
                w_cols = st.columns(4)
                updated_scores = {}
                for i, feat in enumerate(feats):
                    with w_cols[i % 4]:
                        updated_scores[feat] = st.slider(feat.replace("_", " "), 0.0, 10.0, float(cleaned[feat]), 0.5)
                
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Predict with New Scores 🔮", width='stretch')
                if submitted:
                    new_prediction = ml_model.predict(pd.DataFrame([updated_scores])[feats])
                    if new_prediction[0] == 1:
                        st.success("🎉 If you achieve these scores, you will be **LIKELY PLACED**!")
                        st.balloons()
                    else:
                        st.error("📉 Even with these simulated scores, the model requires more improvement.")
                        
        with tab3:
            st.subheader("🎯 Auto-Generated Job Matches")
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 8, 68, 0.3); padding: 2rem; border-radius: 16px; backdrop-filter: blur(10px); box-shadow: 0 8px 32px rgba(255, 8, 68, 0.1);">
                {matches}
            </div>
            """, unsafe_allow_html=True)