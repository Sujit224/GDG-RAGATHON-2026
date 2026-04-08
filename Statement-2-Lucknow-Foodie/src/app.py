from data_loader import load_data
from hybrid_search import hybrid_search
from query_understanding import parse_query

def main():
    df = load_data("../dataset/restaurants.csv")

    if df is None:
        return

    print("🚀 Lucknow Foodie (Smart Search)\n")

    while True:
        query = input("Enter your query (or 'exit'): ")

        if query.lower() == "exit":
            break

        parsed_query, filters = parse_query(query)

        results = hybrid_search(df, parsed_query, filters)

        if results.empty:
            print("❌ No results found\n")
        else:
            print("\nTop Results:\n")
            for _, row in results.head(5).iterrows():
                print(f"{row['name']} | {row['location']} | ⭐ {row['rating']} | ₹{row['price_for_two']}")
            print()

if __name__ == "__main__":
    main()