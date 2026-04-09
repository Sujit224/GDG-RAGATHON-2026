from data_loader import load_data
from hybrid_search import hybrid_search
from query_understanding import parse_query
from rag_response import generate_response
from rag_llm import generate_llm_response

def main():
    df = load_data("../dataset/restaurants.csv")

    if df is None:
        return

    print("Lucknow Foodie Guide (RAG Powered)\n")

    while True:
        query = input("Enter your query (or 'exit'): ")

        if query.lower() == "exit":
            break

        parsed_query, filters = parse_query(query)

        results = hybrid_search(df, parsed_query, filters)
        response = generate_llm_response(results.head(5), query)
        print("\n" + response + "\n")
        

if __name__ == "__main__":
    main()