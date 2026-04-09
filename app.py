from __future__ import annotations

from pathlib import Path
from importlib import util
import re
import sys
from typing import Any

import pandas as pd
import streamlit as st


ROOT_DIR = Path(__file__).resolve().parent
INSURANCE_MAIN = ROOT_DIR / "Statement-1-Insurance-Decoder" / "src" / "main.py"
FOODIE_HYBRID = ROOT_DIR / "Statement-2-Lucknow-Foodie" / "src" / "hybrid_search.py"
PLACEMENT_PARSER = ROOT_DIR / "Statement-3-Placement-Predictor" / "src" / "parser.py"
PLACEMENT_PREDICTOR = ROOT_DIR / "Statement-3-Placement-Predictor" / "src" / "predictor.py"
PLACEMENT_MATCHER = ROOT_DIR / "Statement-3-Placement-Predictor" / "src" / "matcher.py"


st.set_page_config(
    page_title="GDG RAGATHON 2026 | AI Systems Showcase",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 1.2rem;
        max-width: 1200px;
    }
    .stButton > button {
        border-radius: 12px;
        border: 1px solid rgba(120, 120, 120, 0.35);
        padding: 0.45rem 0.95rem;
        font-weight: 600;
    }
    .pill {
        display: inline-block;
        padding: 0.18rem 0.55rem;
        border-radius: 999px;
        border: 1px solid rgba(120, 120, 120, 0.35);
        margin-right: 0.35rem;
        margin-bottom: 0.35rem;
        font-size: 0.80rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _load_module(module_name: str, file_path: Path):
    spec = util.spec_from_file_location(module_name, str(file_path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module at {file_path}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@st.cache_resource(show_spinner=False)
def get_insurance_decoder():
    module = _load_module("insurance_main", INSURANCE_MAIN)
    return module.FinePrintDecoder()


@st.cache_resource(show_spinner=False)
def get_foodie_engine():
    module = _load_module("foodie_hybrid", FOODIE_HYBRID)
    return module.LucknowFoodieHybridSearch()


@st.cache_resource(show_spinner=False)
def get_predictor_pipeline():
    module = _load_module("placement_predictor", PLACEMENT_PREDICTOR)
    return module.train_model()


def extract_citations(text: str) -> tuple[str, str]:
    section = re.search(r"\bSection\s+([A-Za-z0-9.\-]+)", text, flags=re.IGNORECASE)
    clause = re.search(r"\bClause\s+([A-Za-z0-9.\-]+)", text, flags=re.IGNORECASE)
    section_value = section.group(1) if section else "Not found"
    clause_value = clause.group(1) if clause else "Not found"
    return section_value, clause_value


def render_statement_1() -> None:
    st.title("🛡️ Statement 1 · The Fine Print Decoder")
    st.subheader("High-stakes insurance reasoning with citation-first retrieval")
    st.divider()

    if "s1_messages" not in st.session_state:
        st.session_state.s1_messages = [
            {
                "role": "assistant",
                "avatar": "🤖",
                "content": (
                    "Hi! Ask any policy question. I will keep answers ELI5 and attach Section/Clause evidence "
                    "from retrieved policy chunks."
                ),
            }
        ]

    for message in st.session_state.s1_messages:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.markdown(message["content"])

    question = st.chat_input("Ask an insurance fine-print question...")
    if not question:
        return

    st.session_state.s1_messages.append({"role": "user", "avatar": "🧑‍💼", "content": question})
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🧠"):
        with st.status("🔎 Retrieving policy evidence...", expanded=False):
            decoder = get_insurance_decoder()
            result = decoder.retrieve(question)

        if not result.retrieved_chunks:
            answer = "I could not find relevant policy context for this question."
            st.warning(answer)
            st.session_state.s1_messages.append({"role": "assistant", "avatar": "🧠", "content": answer})
            return

        top_chunk = result.retrieved_chunks[0]
        sec, cl = extract_citations(top_chunk.page_content)
        eli5_answer = (
            f"Think of insurance like a rulebook. For your question, the closest rule says: "
            f"**{top_chunk.page_content[:280]}...**"
        )
        citation_text = f"**Policy Citations:** Section {sec} · Clause {cl}"
        st.markdown(eli5_answer)
        st.markdown(citation_text)

        with st.expander("View retrieved evidence snippets"):
            for idx, chunk in enumerate(result.retrieved_chunks[:3], start=1):
                chunk_sec, chunk_cl = extract_citations(chunk.page_content)
                page = chunk.metadata.get("page", "unknown") if isinstance(chunk.metadata, dict) else "unknown"
                st.markdown(f"**Chunk {idx}** · Page {page} · Section {chunk_sec} · Clause {chunk_cl}")
                st.caption(chunk.page_content[:420] + "...")

        assistant_text = f"{eli5_answer}\n\n{citation_text}"
        st.session_state.s1_messages.append({"role": "assistant", "avatar": "🧠", "content": assistant_text})
        st.toast("Fine print decoded with evidence.", icon="✅")


def render_restaurant_card(restaurant: dict[str, Any]) -> None:
    with st.container(border=True):
        st.markdown(f"### {restaurant.get('name', 'Unknown Eatery')}")
        budget = str(restaurant.get("budget", "n/a")).title()
        vibe = str(restaurant.get("vibe", "n/a"))
        veg_text = "Veg" if restaurant.get("is_veg") else "Non-Veg"
        st.markdown(
            f"<span class='pill'>💸 {budget}</span>"
            f"<span class='pill'>🎯 {veg_text}</span>"
            f"<span class='pill'>✨ {vibe}</span>",
            unsafe_allow_html=True,
        )

        dishes = ", ".join(restaurant.get("signature_dishes", []))
        st.write(f"**Signature Dishes:** {dishes if dishes else 'Not available'}")
        score = restaurant.get("score")
        if score is not None:
            st.caption(f"Semantic Match Score: {float(score):.3f}")

        with st.expander("Read diner reviews"):
            reviews = restaurant.get("reviews", [])
            if not reviews:
                st.write("- No reviews available.")
            for review in reviews:
                st.write(f"- {review}")


def render_statement_2() -> None:
    st.title("🍽️ Statement 2 · Lucknow Foodie Guide")
    st.subheader("Hybrid Search: Dense semantic matching + strict metadata filters")
    st.divider()

    col1, col2, col3 = st.columns([2.2, 1, 1], gap="large")
    with col1:
        query = st.text_input("What are you craving?", "Suggest a budget-friendly Biryani place")
    with col2:
        budget = st.selectbox("Budget", ["any", "budget", "mid", "premium"], index=1)
    with col3:
        veg_pref = st.selectbox("Diet Preference", ["any", "veg", "non-veg"], index=2)

    if st.button("🔍 Find Restaurants", use_container_width=True):
        with st.spinner("Embedding vibe, applying hard filters, and ranking places..."):
            engine = get_foodie_engine()
            budget_filter = None if budget == "any" else budget
            veg_filter = None if veg_pref == "any" else (veg_pref == "veg")
            matches = engine.hybrid_search(query=query, budget=budget_filter, is_veg=veg_filter, limit=6)

        if not matches:
            st.warning("No restaurants match this combination. Try relaxing one filter.")
            return

        st.success(f"Found {len(matches)} curated match(es).")
        st.toast("Hybrid search completed.", icon="🍽️")

        cards_per_row = 3
        for i in range(0, len(matches), cards_per_row):
            row = matches[i : i + cards_per_row]
            columns = st.columns(cards_per_row, gap="large")
            for col, restaurant in zip(columns, row):
                with col:
                    render_restaurant_card(restaurant)


def render_statement_3() -> None:
    st.title("🎓 Statement 3 · Placement Predictor & Mentor")
    st.subheader("Resume parsing + readiness regression + smart mentor matching")
    st.divider()

    parser_module = _load_module("placement_parser", PLACEMENT_PARSER)
    matcher_module = _load_module("placement_matcher", PLACEMENT_MATCHER)

    uploaded_resume = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    manual_stack = st.text_input("Optional Tech Stack override (comma-separated)", "")

    if uploaded_resume and st.button("🚀 Analyze Candidate Profile", use_container_width=True):
        temp_resume_path = ROOT_DIR / "Statement-3-Placement-Predictor" / "data" / "_uploaded_resume_temp.pdf"
        temp_resume_path.write_bytes(uploaded_resume.getbuffer())

        try:
            with st.spinner("Extracting Resume Entities..."):
                extracted = parser_module.parse_resume_pdf(temp_resume_path)

            if manual_stack.strip():
                extracted["tech_stack"] = [item.strip() for item in manual_stack.split(",") if item.strip()]

            with st.status("📈 Training and scoring readiness...", expanded=False):
                pipeline = get_predictor_pipeline()
                predictor_module = _load_module("placement_predictor_runtime", PLACEMENT_PREDICTOR)
                readiness_score = predictor_module.predict_readiness_score(extracted, trained_pipeline=pipeline)

            with st.spinner("Embedding Tech Stack and finding mentor matches..."):
                tech_stack = extracted.get("tech_stack", [])
                top_matches = matcher_module.find_top_experience_matches(tech_stack, top_k=3) if tech_stack else []

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("CGPA", f"{float(extracted.get('cgpa') or 0):.2f}")
            c2.metric("Tech Skills", str(len(extracted.get("tech_stack", []))))
            c3.metric("Projects", str(len(extracted.get("projects", []))))
            c4.metric("Internships", str(len(extracted.get("internships", []))))

            d1, d2 = st.columns([1.2, 2], gap="large")
            with d1:
                st.metric("Readiness Score", f"{readiness_score}/100")
                has_open_source = bool(extracted.get("open_source_experience"))
                st.metric("Open Source", "Yes" if has_open_source else "No")
            with d2:
                st.markdown("#### Parsed Resume Highlights")
                st.write(f"**Tech Stack:** {', '.join(extracted.get('tech_stack', [])) or 'Not detected'}")
                st.write(f"**Projects:** {len(extracted.get('projects', []))} listed")
                st.write(f"**Internships:** {len(extracted.get('internships', []))} listed")
                if extracted.get("open_source_experience"):
                    st.write("**Open Source Signals:**")
                    for item in extracted["open_source_experience"][:3]:
                        st.write(f"- {item}")

            st.markdown("#### 🎯 Top 3 Smart Experience Matches")
            if not top_matches:
                st.info("No stack detected for matching yet. Add stack manually and rerun.")
            else:
                st.dataframe(pd.DataFrame(top_matches), use_container_width=True, hide_index=True)

            st.success("Placement analysis completed successfully.")
            st.toast("Candidate profile analyzed perfectly.", icon="✅")
        finally:
            if temp_resume_path.exists():
                temp_resume_path.unlink()


def main() -> None:
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        selected = st.radio(
            "Choose a module",
            options=[
                "🛡️ Statement 1: Fine Print Decoder",
                "🍽️ Statement 2: Lucknow Foodie Guide",
                "🎓 Statement 3: Placement Predictor",
            ],
            label_visibility="collapsed",
        )
        st.divider()
        st.caption("Built for GDG RAGATHON 2026")

    if selected.startswith("🛡️"):
        render_statement_1()
    elif selected.startswith("🍽️"):
        render_statement_2()
    else:
        render_statement_3()


if __name__ == "__main__":
    main()
