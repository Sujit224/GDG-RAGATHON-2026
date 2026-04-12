import streamlit as st
import os
from src.extractor import ProfileExtractor, StudentProfile
from src.predictor import PlacementPredictor
from src.rag_engine import ExperienceMatcher

# Page config
st.set_page_config(
    page_title="Placement Predictor & Mentor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
    }
    .score-large {
        font-size: 3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'profile' not in st.session_state:
    st.session_state.profile = None
if 'score' not in st.session_state:
    st.session_state.score = None
if 'experiences' not in st.session_state:
    st.session_state.experiences = None

# Check for API key
def check_api_key():
    if "GROQ_API_KEY" in st.secrets:
        os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
        return True
    elif "GROQ_API_KEY" in os.environ:
        return True
    return False

if not check_api_key():
    st.error("❌ Groq API Key Not Found!")
    st.info("""
    **Setup Instructions:**
    
    1. Get your API key from https://console.groq.com
    2. Create `.streamlit/secrets.toml` in project root:
       ```
       GROQ_API_KEY = "your_api_key_here"
       ```
    3. Restart the app
    """)
    st.stop()

# Initialize components
@st.cache_resource
def load_components():
    extractor = ProfileExtractor()
    predictor = PlacementPredictor()
    matcher = ExperienceMatcher()
    return extractor, predictor, matcher

extractor, predictor, matcher = load_components()

# Title
st.markdown('<div class="main-title">🎓 Placement Predictor & Mentor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Career Readiness Assessment</div>', unsafe_allow_html=True)

# Tabs
tab1, tab2 = st.tabs(["Chat-Based", "Resume Upload"])

# Tab 1: Chat-Based
with tab1:
    st.header("Tell Us About Yourself")
    st.write("Describe your profile in natural language")
    
    user_input = st.text_area(
        "Your details:",
        placeholder="Example: My CGPA is 8.5, I know Python, Java, and React. I've done 3 projects, 2 internships, my communication is good, and I have open source experience.",
        height=120
    )
    
    if st.button("Extract Profile", key="chat_button"):
        if user_input.strip():
            with st.spinner("Extracting profile..."):
                try:
                    st.session_state.profile = extractor.extract_from_text(user_input)
                    st.success("Profile extracted successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter your details!")

# Tab 2: Resume Upload
with tab2:
    st.header("Upload Your Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX file",
        type=["pdf", "docx"],
        key="resume_upload"
    )
    
    if st.button("Upload & Extract", key="resume_button"):
        if uploaded_file is not None:
            with st.spinner("Processing resume..."):
                try:
                    import tempfile
                    import os
                    
                    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name
                    
                    text = extractor.parse_resume(tmp_path)
                    st.session_state.profile = extractor.extract_from_text(text)
                    os.unlink(tmp_path)
                    st.success("Resume processed successfully!")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please upload a file!")

# Display Results
if st.session_state.profile:
    st.divider()
    st.header("📊 Your Profile Analysis")
    
    profile = st.session_state.profile
    
    # Profile details in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("CGPA", f"{profile.cgpa:.2f}")
    with col2:
        st.metric("Projects", profile.projects_count)
    with col3:
        st.metric("Internships", profile.internships_count)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Communication", f"{profile.communication_score}/10")
    with col2:
        st.metric("Open Source", "Yes" if profile.opensource_experience else "No")
    
    # Tech Stack
    st.subheader("Tech Stack")
    if profile.tech_stack:
        tech_cols = st.columns(len(profile.tech_stack))
        for i, tech in enumerate(profile.tech_stack):
            with tech_cols[i]:
                st.info(f"🔧 {tech}")
    else:
        st.info("No tech stack identified")
    
    # Predict button
    st.divider()
    
    if st.button("Get Readiness Score & Recommendations", key="predict_button"):
        with st.spinner("Analyzing your profile..."):
            try:
                # Get score
                score = predictor.predict(profile)
                st.session_state.score = score
                
                # Get experiences
                experiences = matcher.match_experiences(profile.tech_stack)
                st.session_state.experiences = experiences
                
                st.success("Analysis complete!")
            except Exception as e:
                st.error(f"Error: {str(e)}")
    
    # Display Results
    if st.session_state.score is not None:
        st.divider()
        st.header("🎯 Results")
        
        # Score display
        score = st.session_state.score
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown(f'<div class="metric-card"><div class="score-large">{int(score)}</div><div>/100</div></div>', unsafe_allow_html=True)
        
        with col2:
            if score >= 80:
                message = "🌟 Excellent! Ready for top companies"
                color = "green"
            elif score >= 60:
                message = "💪 Good readiness, keep improving"
                color = "blue"
            else:
                message = "📚 Good foundation, more practice needed"
                color = "orange"
            
            st.markdown(f"<h3 style='color: {color};'>{message}</h3>", unsafe_allow_html=True)
        
        # Recommended experiences
        if st.session_state.experiences:
            st.subheader("📚 Recommended Interview Experiences")
            
            for i, exp in enumerate(st.session_state.experiences, 1):
                with st.expander(f"{i}. {exp['company']}", expanded=(i==1)):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(exp['content'])
                    
                    with col2:
                        st.metric("Difficulty", f"{exp.get('difficulty', 5)}/10")
                    
                    if exp.get('tech_stack'):
                        st.caption(f"Tech: {exp['tech_stack']}")
        else:
            st.info("No matching experiences found")
    
    # Reset button
    st.divider()
    if st.button("Start Over", key="reset_button"):
        st.session_state.profile = None
        st.session_state.score = None
        st.session_state.experiences = None
        st.rerun()
