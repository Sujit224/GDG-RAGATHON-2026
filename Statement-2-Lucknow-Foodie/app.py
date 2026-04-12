import json
import re
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Lucknow Foodie Guide 🍢",
    page_icon="🍢",
    layout="wide",
)

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    with open("dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["outlets"]

outlets = load_data()

# ─────────────────────────────────────────────
# BUILD TF-IDF INDEX (Semantic-like search)
# ─────────────────────────────────────────────
@st.cache_resource
def build_tfidf_index(outlets):
    corpus = []
    for o in outlets:
        text = (
            o["name"] + " "
            + o["area"] + " "
            + " ".join(o["speciality"]) + " "
            + " ".join(o["tags"]) + " "
            + o["description"]
        )
        corpus.append(text.lower())
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(corpus)
    return vectorizer, tfidf_matrix

vectorizer, tfidf_matrix = build_tfidf_index(outlets)

# ─────────────────────────────────────────────
# HYBRID SEARCH FUNCTION
# ─────────────────────────────────────────────
def keyword_search(query, outlets, top_k=15):
    """Exact keyword match on name, tags, speciality, area."""
    q = query.lower().strip()
    scores = []
    for i, o in enumerate(outlets):
        score = 0
        searchable = (
            o["name"].lower()
            + " ".join(o["tags"])
            + " ".join(o["speciality"]).lower()
            + o["area"].lower()
        )
        words = re.findall(r'\w+', q)
        for word in words:
            if word in searchable:
                score += 1
        scores.append((i, score))
    return scores  # list of (index, score)


def semantic_search(query, top_k=15):
    """TF-IDF cosine similarity search."""
    q_vec = vectorizer.transform([query.lower()])
    sims = cosine_similarity(q_vec, tfidf_matrix).flatten()
    scores = [(i, float(sims[i])) for i in range(len(outlets))]
    return scores


def hybrid_search(query, filters=None, alpha=0.5, top_k=10):
    """
    Combines keyword + semantic scores.
    alpha=0.5 means equal weight. 
    filters: dict with optional keys: veg, area
    """
    kw_scores = dict(keyword_search(query, outlets))
    sem_scores = dict(semantic_search(query))

    # Normalize
    kw_max = max(kw_scores.values()) or 1
    sem_max = max(sem_scores.values()) or 1

    combined = {}
    for i in range(len(outlets)):
        kw = kw_scores.get(i, 0) / kw_max
        sem = sem_scores.get(i, 0) / sem_max
        combined[i] = alpha * kw + (1 - alpha) * sem

    # Sort
    ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)

    # Apply filters
    results = []
    for idx, score in ranked:
        o = outlets[idx]
        if filters:
            diet = filters.get("diet", "All")
            if diet == "Veg Only" and not o["veg"]:
                continue
            if diet == "Non-Veg Only" and o["veg"]:
                continue
            if filters.get("area") and filters["area"] != "All Areas":
                if filters["area"].lower() not in o["area"].lower():
                    continue
        if score > 0.01:
            results.append((o, round(score * 100, 1)))

    return results[:top_k]

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Super Vibrant Animated Background */
    .stApp { 
        background: linear-gradient(-45deg, #FF9A9E, #FECFEF, #F6D365, #FFB199);
        background-size: 400% 400%;
        animation: gradientBG 12s ease infinite;
    }
    
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* GLOBAL READABILITY FIX: Prevent native dark-theme white text from vanishing into the vibrant light background */
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricLabel"] p,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] span,
    [data-testid="stWidgetLabel"] p {
        color: #1a202c !important;
        font-weight: 700 !important;
    }

    .main-title { 
        font-size: 4.5rem; 
        font-weight: 900; 
        color: #ffffff !important;
        text-align: center; 
        margin-bottom: 0px;
        line-height: 1.1;
        text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.15), 0 0 30px rgba(255, 255, 255, 0.6);
    }
    .subtitle { 
        font-size: 1.5rem; 
        text-align: center; 
        color: #ffffff !important; 
        margin-bottom: 3rem; 
        font-weight: 800;
        text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.2);
    }
    
    /* Premium Glassmorphic Cards (High Contrast) */
    .card { 
        background: rgba(255, 255, 255, 0.85); /* Much more opaque so text is visible */
        border: 2px solid rgba(255, 255, 255, 1);
        border-radius: 20px; 
        padding: 1.8rem; 
        margin-bottom: 1.8rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); 
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .card:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 15px 45px rgba(255, 65, 108, 0.25); 
        border-color: #ff416c;
        background: rgba(255, 255, 255, 0.95);
    }
    
    .outlet-name { 
        font-size: 1.8rem; 
        font-weight: 900; 
        color: #1a202c !important; 
        margin-bottom: 0.5rem;
    }
    
    .card p, .card div {
        color: #2d3748 !important; /* Force all card text to be readable dark gray */
        font-weight: 600;
    }

    .score-badge { 
        background: linear-gradient(135deg, #F56565 0%, #C53030 100%); 
        color: white !important; 
        border-radius: 24px;
        padding: 5px 14px; 
        font-size: 0.9rem; 
        font-weight: 800; 
        float: right; 
        box-shadow: 0 4px 15px rgba(197, 48, 48, 0.3);
    }
    
    /* Modern Tag Pills */
    .tag { 
        display: inline-block; 
        background: #edf2f7; 
        color: #2b6cb0 !important;
        border-radius: 12px; 
        padding: 6px 14px; 
        font-size: 0.85rem;
        margin: 5px 5px 0 0; 
        font-weight: 800; 
        border: 1px solid #bee3f8;
        transition: all 0.2s ease;
    }
    .tag:hover {
        background: #2b6cb0;
        color: #ffffff !important;
        transform: translateY(-2px);
    }
    
    .veg-badge { 
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); 
        color: white !important; 
        border-radius: 12px;
        padding: 4px 12px; 
        font-size: 0.85rem; 
        font-weight: 800;
        box-shadow: 0 4px 10px rgba(72, 187, 120, 0.3);
    }
    .nonveg-badge { 
        background: linear-gradient(135deg, #fc8181 0%, #e53e3e 100%); 
        color: white !important; 
        border-radius: 12px;
        padding: 4px 12px; 
        font-size: 0.85rem; 
        font-weight: 800; 
        box-shadow: 0 4px 10px rgba(229, 62, 62, 0.3);
    }
    
    /* Thick modern inputs */
    .stTextInput input {
        border-radius: 16px !important;
        border: 3px solid rgba(255, 255, 255, 0.9) !important;
        padding: 1rem 1.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        color: #1a202c !important;
        background: rgba(255, 255, 255, 0.95) !important;
        box-shadow: 0 8px 30px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }
    .stTextInput input::placeholder {
        color: #718096 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus {
        border-color: #ff4b2b !important;
        box-shadow: 0 8px 35px rgba(255, 75, 43, 0.3) !important;
        transform: scale(1.02);
    }
    
    /* Vibrant Sidebar & Fix Invisible Text */
    [data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.85); /* High opacity for text contrast */
        backdrop-filter: blur(25px);
        border-right: 2px solid rgba(255, 255, 255, 1);
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label {
        color: #0f172a !important; /* Ensure labels are dark against white sidebar */
        font-weight: 700 !important;
    }
    
    /* Make the Area text explicitly readable regardless of baseweb hierarchy */
    .stSelectbox *, .stRadio * {
        color: #e53e3e !important; 
        font-weight: 800 !important;
    }
    
    .stSelectbox label, .stRadio label {
        color: #0f172a !important; 
    }
    
    /* Super Punchy Buttons */
    [data-testid="stButton"] button {
        border-radius: 50px;
        font-weight: 900;
        padding: 0.6rem 1.5rem;
        background: rgba(255, 255, 255, 0.95);
        border: 2px solid #ff4b2b;
        color: #ff4b2b !important;
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 6px 15px rgba(0,0,0,0.1);
    }
    [data-testid="stButton"] button:hover {
        background: #ff4b2b;
        color: #ffffff !important;
        border-color: #ff4b2b;
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 10px 25px rgba(255, 75, 43, 0.4);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🍢 Lucknow Foodie Guide</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Nawabo ki City ka Best Khaana Dhundo <br/> <span style="font-size: 0.95rem; font-weight: 400;">Hybrid AI Search with Keyword + Semantic</span></div>', unsafe_allow_html=True)

# ─── SEARCH BAR ───
import random

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    query = st.text_input(
        "🔍 Kya khana hai? (e.g. 'spicy kebab from old lucknow', 'sweet veg snack', 'biryani')",
        placeholder="Type anything in English or Hinglish...",
        label_visibility="collapsed"
    )

with col2:
    search_btn = st.button("Search 🚀", use_container_width=True)

with col3:
    lucky_btn = st.button("Feeling Lucky 🎲", use_container_width=True)

if lucky_btn:
    # Pick a random top-rated spot
    top_spots = [o for o in outlets if float(o["rating"]) >= 4.0]
    random_spot = random.choice(top_spots)
    query = random_spot["name"]
    search_btn = True

# ─── SIDEBAR FILTERS & STATS ───
st.sidebar.header("🎯 Explore Controls")
with st.sidebar.expander("⚙️ Refine Search", expanded=True):
    diet_pref = st.radio("🥦 Diet Preference", ["All", "Veg Only", "Non-Veg Only"])
    areas = ["All Areas"] + sorted(set(o["area"].split(",")[0].strip() for o in outlets))
    selected_area = st.selectbox("📍 Area", areas)
    alpha = st.slider("⚖️ Match Type", 0.0, 1.0, 0.5, 0.1, help="0 = Semantic (Meaning), 1 = Keyword (Exact)")

st.sidebar.markdown("---")
st.sidebar.header("📊 Database Stats")
colA, colB = st.sidebar.columns(2)
colA.metric("Total Spots", len(outlets))
colB.metric("Veg Only", sum(1 for o in outlets if o["veg"]))
st.sidebar.metric("Average Rating", f"{np.mean([float(o['rating']) for o in outlets]):.1f} ⭐")

# ─── QUICK SUGGESTION BUTTONS ───
st.markdown("**Quick Searches:**")
suggestions = [
    "🍖 Galouti Kebab", "🍚 Biryani", "🧆 Street Food",
    "🌿 Veg Breakfast", "🍮 Sweets & Desserts", "🥘 Nihari"
]
s_cols = st.columns(len(suggestions))
for i, sug in enumerate(suggestions):
    if s_cols[i].button(sug, use_container_width=True):
        query = sug.split(" ", 1)[1]  # strip emoji
        search_btn = True

st.divider()

# ─── RESULTS ───
if query and (search_btn or query):
    filters = {"diet": diet_pref, "area": selected_area}
    results = hybrid_search(query, filters=filters, alpha=alpha)

    if results:
        st.markdown(f"### 🍽️ Top Results for **'{query}'**")
        for outlet, score in results:
            veg_label = '<span class="veg-badge">🟢 VEG</span>' if outlet["veg"] else '<span class="nonveg-badge">🔴 NON-VEG</span>'
            tags_html = " ".join(f'<span class="tag">{t}</span>' for t in outlet["tags"][:6])
            st.markdown(f"""
<div class="card">
  <div>
    <span class="score-badge">Match: {score}%</span>
    <span class="outlet-name">{outlet["name"]}</span>
    &nbsp; {veg_label}
  </div>
  <div style="color:#7f8c8d; font-size:0.9rem; margin: 4px 0;">📍 {outlet["area"]} &nbsp;|&nbsp; ⭐ {outlet["rating"]} &nbsp;|&nbsp; 💰 {outlet["price_range"]} &nbsp;|&nbsp; 🕐 {outlet["timing"]}</div>
  <p style="margin: 6px 0; color: #34495e;">{outlet["description"]}</p>
  <div><b>Must Try:</b> 🌟 {outlet["must_try"]}</div>
  <div style="margin-top:6px;">{tags_html}</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.warning("Koi result nahi mila! Try karo 'kebab', 'biryani', 'sweets' etc.")

# ─── DEFAULT: Show all ───
elif not query:
    st.markdown("### 🗺️ All Lucknow Food Spots")
    cols = st.columns(3)
    
    # Pre-filter all outlets based on sidebar
    filtered_outlets = []
    for o in outlets:
        if diet_pref == "Veg Only" and not o["veg"]:
            continue
        if diet_pref == "Non-Veg Only" and o["veg"]:
            continue
        if selected_area != "All Areas" and selected_area.lower() not in o["area"].lower():
            continue
        filtered_outlets.append(o)
        
    if not filtered_outlets:
        st.warning("No spots match your current filters. Try relaxing them!")

    for i, o in enumerate(filtered_outlets):
        with cols[i % 3]:
            veg_icon = "🟢" if o["veg"] else "🔴"
            st.markdown(f"""
<div class="card">
  <div class="outlet-name">{veg_icon} {o["name"]}</div>
  <div style="color:#7f8c8d; font-size:0.85rem;">📍 {o["area"]} | ⭐ {o["rating"]}</div>
  <div style="color:#e67e22; font-size:0.85rem;">🌟 {o["must_try"]}</div>
  <div style="color:#636e72; font-size:0.8rem;">💰 {o["price_range"]}</div>
</div>
""", unsafe_allow_html=True)

# ─── FOOTER ───
st.divider()
st.markdown("""
<div style="text-align:center; color:#b2bec3; font-size:0.85rem;">
  Built with ❤️ | Hybrid Search: TF-IDF Semantic + Keyword Matching | Data: Lucknow's Finest 15 Spots
</div>
""", unsafe_allow_html=True)
