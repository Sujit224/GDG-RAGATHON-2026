import fitz # PyMuPDF
import pandas as pd

def inspect_pdf():
    doc = fitz.open('data/INTERVIEW EXPERIENCES.pdf')
    print(f"Total Pages: {len(doc)}")
    print("--- First Page Text ---")
    print(doc[0].get_text()[:500])
    print("...")

def inspect_csv():
    df = pd.read_csv('data/normalized_placement_data.csv')
    print("--- CSV Info ---")
    print(df.info())
    print("--- CSV Head ---")
    print(df.head(2))

if __name__ == '__main__':
    try:
        inspect_pdf()
    except Exception as e:
        print("PDF Error:", e)
    try:
        inspect_csv()
    except Exception as e:
        print("CSV Error:", e)
