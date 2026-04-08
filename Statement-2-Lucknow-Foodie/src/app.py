from data_loader import load_data
from keyword_search import keyword_search

def main():
    df = load_data("../dataset/restaurants.csv")

    if df is None:
        return

    print("🍽️ Lucknow Foodie (Keyword Search)\n")

    while True:
        query = input("Enter your query (or 'exit'): ")

        if query.lower() == "exit":
            break

        results = keyword_search(df, query)

        if results.empty:
            print("❌ No results found\n")
        else:
            print("\nTop Results:\n")
            for _, row in results.iterrows():
                print(f"{row['name']} | {row['location']} | ⭐ {row['rating']} | ₹{row['price_for_two']}")
            print()

if __name__ == "__main__":
    main()