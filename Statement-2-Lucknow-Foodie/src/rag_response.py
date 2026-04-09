def generate_response(results, query):
    if results.empty:
        return "Sorry, no good matches found."

    response = f"\nRecommendations for: '{query}'\n\n"

    for _, row in results.iterrows():
        response += f"- {row['name']} ({row['location']})\n"
        response += f"  Rating: {row['rating']} | Price for two: INR {row['price_for_two']}\n"
        response += f"  Must try: {row['signature_dish']}\n"
        response += f"  Vibe: {row['vibe']} | {row['veg_nonveg']}\n\n"

    return response