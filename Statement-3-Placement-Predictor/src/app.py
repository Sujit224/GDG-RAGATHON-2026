import streamlit as st
from extractor import extract_from_text
from rag_engine import calculate_readiness_score

st.set_page_config(page_title="Placement Predictor", layout="centered")

st.title("🚀 Placement Readiness Predictor")

# -----------------------------
# Option Selection
# -----------------------------
option = st.radio(
    "Choose Input Method",
    ["Paste Resume", "Manual Input"]
)

data = None

# -----------------------------
# OPTION 1: Resume Input
# -----------------------------
if option == "Paste Resume":
    resume_text = st.text_area("Paste your resume here")

    if st.button("Analyze Resume"):
        if resume_text.strip() == "":
            st.warning("Please paste your resume")
        else:
            data = extract_from_text(resume_text)

# -----------------------------
# OPTION 2: Manual Input
# -----------------------------
elif option == "Manual Input":
    cgpa = st.slider("CGPA", 0.0, 10.0, 7.0)
    projects = st.number_input("Projects", 0, 10, 1)
    internships = st.number_input("Internships", 0, 5, 0)
    skills = st.number_input("Skills", 0, 20, 3)
    dsa = st.slider("DSA Level", 0, 10, 5)

    if st.button("Calculate Score"):
        data = {
            "cgpa": cgpa,
            "projects": projects,
            "internships": internships,
            "skills": skills,
            "dsa": dsa
        }

# -----------------------------
# RESULT SECTION
# -----------------------------
if data:
    score = calculate_readiness_score(data)

    st.subheader("📊 Extracted Data")
    st.json(data)

    st.subheader("🔥 Readiness Score")
    st.success(f"{score}/100")

    # Feedback
    feedback = []

    if data["projects"] < 2:
        feedback.append("Build more projects")

    if data["internships"] == 0:
        feedback.append("Try getting an internship")

    if data["dsa"] < 5:
        feedback.append("Improve DSA")

    if feedback:
        st.subheader("💡 Suggestions")
        for tip in feedback:
            st.write(f"- {tip}")