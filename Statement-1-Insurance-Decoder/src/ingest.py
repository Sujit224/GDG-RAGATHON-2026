import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document


print("CURRENT DIR:", os.getcwd())
print("DOCS PATH EXISTS:", os.path.exists("../docs"))
print("DOCS ABS PATH:", os.path.abspath("../docs"))
print("FILES:", os.listdir("../docs") if os.path.exists("../docs") else "NO FOLDER")

DOCS_PATH = "../docs"
DB_PATH = "../vectorstore"


def load_docs():
    docs = []

    for file in os.listdir(DOCS_PATH):
        if file.endswith(".pdf"):
            path = os.path.join(DOCS_PATH, file)
            print(f"📄 Reading: {path}")

            reader = PdfReader(path)

            for i, page in enumerate(reader.pages):
                text = page.extract_text()

                if text and text.strip():
                    docs.append(
                        Document(
                            page_content=text,
                            metadata={"page": i + 1}
                        )
                    )

    return docs


def main():
    docs = load_docs()
    print(f"✅ Pages loaded: {len(docs)}")

    if len(docs) == 0:
        print("❌ No text extracted → check PDF")
        return

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)
    print(f"✅ Chunks created: {len(chunks)}")

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(DB_PATH)

    print("🔥 Vector DB created successfully")


if __name__ == "__main__":
    main()