from __future__ import annotations

_MODEL_NAME = "google/flan-t5-small"
_CACHE = {"tokenizer": None, "model": None, "load_error": None}


def _get_llm():
    """
    Lazy-load transformers components.

    This avoids Streamlit's file-watcher importing vision-related optional
    submodules that can require torchvision even for text-only usage.
    """
    if _CACHE["model"] is not None and _CACHE["tokenizer"] is not None:
        return _CACHE["tokenizer"], _CACHE["model"]
    if _CACHE["load_error"] is not None:
        raise _CACHE["load_error"]

    try:
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM  # type: ignore

        tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        model = AutoModelForSeq2SeqLM.from_pretrained(_MODEL_NAME)
        _CACHE["tokenizer"] = tokenizer
        _CACHE["model"] = model
        return tokenizer, model
    except Exception as e:
        _CACHE["load_error"] = e
        raise


def generate_llm_response(results, query):
    if results.empty:
        return "Sorry, I couldn't find good matches."

    # If transformers can't load for any reason, return a deterministic summary.
    try:
        tokenizer, model = _get_llm()
    except Exception:
        return _fallback_from_results(results, query)

    # Build context
    context = ""
    for _, row in results.head(5).iterrows():
        hours = row["hours"] if "hours" in row else ""
        dist = row["distance_from_iiit_km"] if "distance_from_iiit_km" in row else ""
        context += (
            f"{row['name']} in {row['location']} serves {row['cuisine']} cuisine, "
            f"rated {row['rating']} stars, costs ₹{row['price_for_two']}, "
            f"known for {row['signature_dish']}, vibe: {row['vibe']}, "
            f"hours: {hours}, distance_from_iiit_km: {dist}.\n"
        )

    prompt = f"""
You are a smart food assistant.

User query: {query}

Restaurants:
{context}

Recommend the best 2 or 3 places with short reasons.
If the user asks "near IIIT" prioritize smaller distance_from_iiit_km when available.
"""

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True)

    outputs = model.generate(
        **inputs,
        max_new_tokens=140
    )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    formatted = format_output(response)

    # Fallback if model outputs junk/too-short text (common on small models)
    if len(formatted.strip()) < 60:
        return _fallback_from_results(results, query)

    cleaned = formatted.lower()
    top_names = [str(n).lower() for n in results.head(3)["name"].tolist() if str(n).strip()]
    if top_names and not any(n in cleaned for n in top_names):
        return _fallback_from_results(results, query)

    return formatted


def format_output(text):
    cleaned = " ".join(str(text).split())
    return "\nRecommendations:\n\n" + cleaned + "\n"


def _fallback_from_results(results, query):
    top = results.head(3)
    lines = [f"Recommendations for: {query}", ""]
    for _, row in top.iterrows():
        extra = []
        if "hours" in row and str(row["hours"]).strip():
            extra.append(f"hours {row['hours']}")
        if "distance_from_iiit_km" in row and str(row["distance_from_iiit_km"]).strip():
            extra.append(f"{row['distance_from_iiit_km']} km from IIIT")
        extra_txt = f" ({', '.join(extra)})" if extra else ""
        lines.append(
            f"- {row['name']} - {row['location']} | {row['cuisine']} | INR {row['price_for_two']} for two | {row['veg_nonveg']} | try: {row['signature_dish']}{extra_txt}"
        )
    return "\n".join(lines) + "\n"