from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from data_loader import load_data
from hybrid_search import hybrid_search
from query_understanding import parse_query


APP_TITLE = "Lucknow Foodie Guide (IIIT Lucknow)"


def _data_path() -> str:
    base = Path(__file__).resolve().parent.parent  # Statement-2-Lucknow-Foodie/
    return str(base / "dataset" / "restaurants.csv")


def _inject_css():
    st.markdown(
        """
<style>
  /* Page tweaks */
  .block-container { padding-top: 1.25rem; padding-bottom: 2rem; }
  [data-testid="stSidebar"] { border-right: 1px solid rgba(255,255,255,0.08); }

  /* Hero */
  .lf-hero {
    padding: 18px 18px;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(255, 153, 102, 0.22), rgba(255, 87, 34, 0.10), rgba(63, 81, 181, 0.10));
    border: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 14px;
  }
  .lf-hero h1 { margin: 0; font-size: 1.55rem; line-height: 1.25; }
  .lf-hero p  { margin: 6px 0 0 0; opacity: 0.85; }

  /* Cards */
  .lf-card {
    padding: 14px 14px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.03);
    margin: 10px 0 12px 0;
  }
  .lf-title {
    display: flex;
    gap: 10px;
    align-items: baseline;
    justify-content: space-between;
    margin-bottom: 8px;
  }
  .lf-title .name { font-weight: 700; font-size: 1.05rem; }
  .lf-title .loc  { opacity: 0.80; font-size: 0.95rem; }
  .lf-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
  .lf-meta { opacity: 0.9; }

  /* Badges */
  .lf-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.85rem;
    border: 1px solid rgba(255,255,255,0.14);
    background: rgba(255,255,255,0.04);
  }
  .lf-badge.green { border-color: rgba(76,175,80,0.35); background: rgba(76,175,80,0.12); }
  .lf-badge.red { border-color: rgba(244,67,54,0.35); background: rgba(244,67,54,0.12); }
  .lf-badge.blue { border-color: rgba(33,150,243,0.35); background: rgba(33,150,243,0.12); }
  .lf-badge.amber { border-color: rgba(255,193,7,0.35); background: rgba(255,193,7,0.12); }
  .lf-badge.purple { border-color: rgba(156,39,176,0.35); background: rgba(156,39,176,0.12); }

  /* Small helpers */
  .lf-muted { opacity: 0.75; }
</style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_df() -> pd.DataFrame:
    df = load_data(_data_path())
    if df is None:
        return pd.DataFrame()
    return df


def _sidebar_filters(df: pd.DataFrame) -> dict:
    st.sidebar.markdown("### Filters")

    preset = st.sidebar.radio(
        "Quick preset",
        ["Student budget", "Balanced", "Premium"],
        index=1,
        horizontal=True,
    )

    near_iiit = st.sidebar.checkbox("Near IIIT Lucknow", value=True)
    near_radius_km = st.sidebar.slider("Near radius (km)", min_value=2.0, max_value=25.0, value=10.0, step=0.5)

    default_price = 500 if preset == "Student budget" else 900 if preset == "Balanced" else 1800
    default_rating = 3.8 if preset == "Student budget" else 4.0 if preset == "Balanced" else 4.2

    max_price = st.sidebar.slider("Max price for two (INR)", min_value=100, max_value=3000, value=int(default_price), step=50)
    min_rating = st.sidebar.slider("Min rating", min_value=0.0, max_value=5.0, value=float(default_rating), step=0.1)

    veg_choice = st.sidebar.selectbox("Veg preference", ["Any", "Veg", "Non-Veg"], index=0)

    vibe_values = ["Any"]
    if "vibe" in df.columns and not df.empty:
        vibe_values += sorted({str(v).strip() for v in df["vibe"].tolist() if str(v).strip()})
    vibe_choice = st.sidebar.selectbox("Vibe", vibe_values, index=0)

    area_hint = st.sidebar.text_input("Area hint (optional)", placeholder="e.g., Hazratganj / Gomti Nagar / Palassio")

    filters = {
        "location": area_hint.lower().strip() or None,
        "near_iiit": bool(near_iiit),
        "near_radius_km": float(near_radius_km),
        "max_price": int(max_price) if max_price else None,
        "min_rating": float(min_rating) if min_rating else None,
        "veg": None if veg_choice == "Any" else veg_choice,
        "vibe": None if vibe_choice == "Any" else vibe_choice.lower().strip(),
        "dish": None,
    }

    return filters


def _badge(label: str, color: str = "") -> str:
    color_class = f" {color}" if color else ""
    return f"<span class='lf-badge{color_class}'>{label}</span>"


def _price_tag(price_for_two) -> str:
    try:
        p = int(float(price_for_two))
    except Exception:
        return "INR ?"
    if p <= 400:
        return "Budget"
    if p <= 900:
        return "Mid"
    return "Premium"


def _render_results(results: pd.DataFrame):
    if results.empty:
        st.warning("No matches found. Try relaxing filters (increase radius / budget / lower rating).")
        return

    st.caption(f"Showing top {min(10, len(results))} matches")

    for _, row in results.head(10).iterrows():
        name = str(row.get("name", "")).strip()
        location = str(row.get("location", "")).strip()
        cuisine = str(row.get("cuisine", "")).strip()
        vibe = str(row.get("vibe", "")).strip()
        sig = str(row.get("signature_dish", "")).strip()
        veg = str(row.get("veg_nonveg", "")).strip()
        rating = row.get("rating", "")
        price = row.get("price_for_two", "")
        hours = str(row.get("hours", "")).strip()
        dist = row.get("distance_from_iiit_km", "")

        try:
            r = float(rating)
        except Exception:
            r = None
        rating_txt = f"{r:.1f}/5" if isinstance(r, float) else "N/A"

        veg_color = "green" if veg.lower().startswith("veg") else "red" if "non" in veg.lower() else "blue"
        price_band = _price_tag(price)
        price_color = "amber" if price_band == "Budget" else "blue" if price_band == "Mid" else "purple"

        badges = [
            _badge(f"⭐ {rating_txt}", "blue"),
            _badge(f"₹ {price} for two", price_color),
            _badge(f"{veg}", veg_color),
        ]
        if vibe:
            badges.append(_badge(vibe, "purple"))
        if dist != "" and dist is not None:
            badges.append(_badge(f"{dist} km from IIIT", "amber"))

        meta_lines = []
        if cuisine:
            meta_lines.append(f"<span class='lf-meta'><b>Cuisine</b>: {cuisine}</span>")
        if hours:
            meta_lines.append(f"<span class='lf-meta'><b>Hours</b>: {hours}</span>")
        if sig:
            meta_lines.append(f"<span class='lf-meta'><b>Must try</b>: {sig}</span>")

        st.markdown(
            f"""
<div class="lf-card">
  <div class="lf-title">
    <div>
      <div class="name">{name}</div>
      <div class="loc lf-muted">{location}</div>
    </div>
  </div>
  <div class="lf-row">
    {"".join(badges)}
  </div>
  <div class="lf-row" style="margin-top:10px;">
    {"".join(meta_lines)}
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🍴", layout="wide")
    _inject_css()
    st.markdown(
        f"""
<div class="lf-hero">
  <h1>{APP_TITLE}</h1>
  <p>Context-aware recommendations for students around IIIT Lucknow — budget, vibe, veg/non-veg, dishes, and distance.</p>
</div>
        """,
        unsafe_allow_html=True,
    )

    df = _load_df()
    if df.empty:
        st.error("Dataset failed to load. Please verify `dataset/restaurants.csv` exists.")
        return

    filters_ui = _sidebar_filters(df)

    left, right = st.columns([1.4, 1.0])
    with left:
        query = st.text_input(
            "Search",
            placeholder="Try: budget biryani near IIIT / best basket chaat in Hazratganj / quiet cafe near campus",
        )
    with right:
        sort_by = st.selectbox("Sort by", ["Relevance", "Distance (near IIIT)", "Rating", "Price (low to high)"], index=0)

    colA, colB, colC = st.columns([1, 1, 1])
    use_llm = colA.toggle("Show bot summary", value=True)
    top_k = colB.slider("Results", min_value=3, max_value=15, value=10, step=1)
    show_table = colC.toggle("Show table view", value=False)

    if not query:
        st.info("Type a query to get recommendations.")
        return

    parsed_query, filters_nl = parse_query(query)
    merged_filters = {**filters_nl, **filters_ui}

    results = hybrid_search(df, parsed_query, merged_filters)

    if sort_by == "Distance (near IIIT)" and "distance_from_iiit_km" in results.columns:
        results = results.sort_values(by="distance_from_iiit_km", ascending=True)
    elif sort_by == "Rating" and "rating" in results.columns:
        results = results.sort_values(by="rating", ascending=False)
    elif sort_by == "Price (low to high)" and "price_for_two" in results.columns:
        results = results.sort_values(by="price_for_two", ascending=True)

    results = results.head(int(top_k))

    m1, m2, m3 = st.columns(3)
    m1.metric("Matches", len(results))
    if "distance_from_iiit_km" in results.columns and not results.empty:
        try:
            m2.metric("Closest (km)", f"{float(results['distance_from_iiit_km'].min()):.1f}")
        except Exception:
            m2.metric("Closest (km)", "—")
    else:
        m2.metric("Closest (km)", "—")
    if "price_for_two" in results.columns and not results.empty:
        try:
            m3.metric("Cheapest (INR for two)", f"{int(float(results['price_for_two'].min()))}")
        except Exception:
            m3.metric("Cheapest (INR for two)", "—")
    else:
        m3.metric("Cheapest (INR for two)", "—")

    if use_llm:
        from rag_llm import generate_llm_response
        with st.spinner("Generating a short recommendation summary..."):
            summary = generate_llm_response(results.head(5), query)
        st.markdown("### Bot summary")
        st.markdown(f"<div class='lf-card'><div class='lf-muted'>{summary}</div></div>", unsafe_allow_html=True)

    st.markdown("### Matches")
    if show_table:
        cols = [c for c in ["name", "location", "cuisine", "rating", "price_for_two", "signature_dish", "veg_nonveg", "vibe", "hours", "distance_from_iiit_km"] if c in results.columns]
        st.dataframe(results[cols], use_container_width=True, hide_index=True)
    else:
        _render_results(results)


if __name__ == "__main__":
    main()

