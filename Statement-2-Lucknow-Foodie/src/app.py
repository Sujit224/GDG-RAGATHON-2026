from data_loader import load_data

def main():
    df = load_data("../dataset/restaurants.csv")
    
    if df is not None:
        print("\nPreview of dataset:\n")
        print(df.head())

if __name__ == "__main__":
    main()