from data_loader import load_data
from semantic_search import semantic_search

def main():
    df = load_data("../dataset/restaurants.csv")

    if df is None:
        return

    print("🧠 Lucknow Foodie (Semantic Search)\n")

    while True:
        query = input("Enter your query (or 'exit'): ")

        if query.lower() == "exit":
            break

        results = semantic_search(df, query)

        print("\nTop Results:\n")
        for _, row in results.head(5).iterrows():
            print(f"{row['name']} | {row['location']} | ⭐ {row['rating']} | ₹{row['price_for_two']}")
        print()

if __name__ == "__main__":
    main()