# import os

# os.environ["ANONYMIZED_TELEMETRY"] = "False"  
# os.environ["CHROMA_TELEMETRY_IMPL"] = "None"

# import argparse
# import glob
# import re
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from sentence_transformers import SentenceTransformer
# import chromadb

# CHROMA_DB_PATH = "./chroma_db"
# DATA_DIR = "./docs" 
# COLLECTION_NAME = "fine_print"

# def get_chroma_collection():
#     client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
#     collection = client.get_or_create_collection(name=COLLECTION_NAME)
#     return collection

# def ingest_documents():
#     print("Ingesting documents...")
   
#     files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
#     if not files:
#         print(f"❌ No .txt files found in {DATA_DIR}. Please check your folder!")
#         return

#     all_chunks_data = [] 
    
#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=500,
#         chunk_overlap=50
#     )

#     for file_path in files:
#         with open(file_path, "r", encoding="utf-8") as f:
#             content = f.read()
            
#         doc_name = os.path.basename(file_path)
        
        
#         chunks = text_splitter.split_text(content)
        
#         for chunk in chunks:
            
#             section_match = re.search(r"(Section \d+:[^\n]+)", chunk)
#             clause_match = re.search(r"(Clause \d+\.\d+:[^\n]+)", chunk)
            
#             meta_section = section_match.group(1) if section_match else "Unknown Section"
#             meta_clause = clause_match.group(1) if clause_match else "Unknown Clause"
            
           
#             all_chunks_data.append({
#                 "text": chunk,
#                 "metadata": {
#                     "source": doc_name,
#                     "section": meta_section,
#                     "clause": meta_clause
#                 }
#             })
            
    
#     print(f"Loading embedding model... Processing {len(all_chunks_data)} chunks.")
#     embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
#     documents = [d["text"] for d in all_chunks_data]
#     metadatas = [d["metadata"] for d in all_chunks_data]
   
#     ids = [f"id_{i}" for i in range(len(all_chunks_data))]
    
   
#     embeddings = embedder.encode(documents).tolist()
    
#     collection = get_chroma_collection()
    
   
#     collection.add(
#         ids=ids,
#         embeddings=embeddings,
#         metadatas=metadatas,
#         documents=documents
#     )
#     print(f"✅ Successfully ingested {len(all_chunks_data)} chunks into ChromaDB!")

# def query_system(user_query, document_filter=None, topic_filter=None):
#     print("Loading query subsystem...")
#     embedder = SentenceTransformer('all-MiniLM-L6-v2')
#     collection = get_chroma_collection()
    
    
#     query_embedding = embedder.encode([user_query]).tolist() 
    
#     where_clause = {}
#     if document_filter:
#         where_clause["source"] = document_filter
    
    
#     results = collection.query(
#         query_embeddings=query_embedding,
#         n_results=3,
#         where=where_clause if where_clause else None
#     )
    
    
#     if not results["documents"] or not results["documents"][0]:
#         print("No relevant clauses found.")
#         return

   
#     retrieved_texts = results["documents"][0]
#     retrieved_metadatas = results["metadatas"][0]
    
    
#     if topic_filter:
#         filtered_texts = []
#         filtered_metas = []
#         for text, meta in zip(retrieved_texts, retrieved_metadatas):
#             if (topic_filter.lower() in text.lower() or 
#                 topic_filter.lower() in meta["section"].lower() or 
#                 topic_filter.lower() in meta["clause"].lower()):
#                 filtered_texts.append(text)
#                 filtered_metas.append(meta)
#         retrieved_texts = filtered_texts
#         retrieved_metadatas = filtered_metas

#     if not retrieved_texts:
#         print("No clauses match your specific topic filter.")
#         return

#     context = "\n".join(retrieved_texts)
    
   
#     from transformers import pipeline
#     print("Simplifying answer (ELI5)...")
   
#     summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
#     if len(context) > 100:
        
#         summary_result = summarizer(context, max_length=100, min_length=30, do_sample=False)
#         summary = summary_result[0]['summary_text']
#     else:
#         summary = context

#     print("\n" + "="*50)
#     print("🤖 FINE PRINT DECODER:")
#     print("="*50)
#     print(f"Question: {user_query}")
#     if document_filter: print(f"Applies to: {document_filter}")
#     print("\n📝 ELI5 Answer (Simplified):")
#     print(summary)
#     print("\n⚖️ Source Attribution (Bonus Points!):")
#     for meta in retrieved_metadatas:
#         print(f"  - {meta['source']} | {meta['section']} | {meta['clause']}")
#     print("="*50)

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Fine Print Decoder - RAG System")
#     parser.add_argument("action", choices=["ingest", "query"], help="Action to perform")
#     parser.add_argument("--query", type=str, help="Question to ask")
#     parser.add_argument("--filter-doc", type=str, help="Filter by document name")
#     parser.add_argument("--filter-topic", type=str, help="Filter by topic (e.g., coverage)")
    
#     args = parser.parse_args()
    
#     if args.action == "ingest":
#         ingest_documents()
#     elif args.action == "query":
#         if not args.query:
#             print("Please provide a --query!")
#         else:
#             query_system(args.query, args.filter_doc, args.filter_topic)
import os
os.environ["ANONYMIZED_TELEMETRY"] = "False"  # Disable chromadb telemetry
os.environ["CHROMA_TELEMETRY_IMPL"] = "None"
import argparse
import glob
import re
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sentence_transformers import SentenceTransformer
import chromadb

# Ensure paths are relative to the script itself, not where you call it from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_DB_PATH = os.path.join(BASE_DIR, "chroma_db")
DATA_DIR = os.path.join(BASE_DIR, "docs")
COLLECTION_NAME = "fine_print"

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    return collection

def ingest_documents():
    print("Ingesting documents...")
    files = glob.glob(os.path.join(DATA_DIR, "*.txt"))
    
    docs = []
    
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        doc_name = os.path.basename(file_path)
        
        # Simple heuristic to split sections nicely if applicable
        sections = re.split(r"(Section \d+:.*?)\n", content)
        
        current_section_name = "General"
        
        # The split might put empty strings or the match as odd/even.
        # Let's just use RecursiveCharacterTextSplitter
        # but attach custom metadata by scanning each chunk.
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        
        chunks = text_splitter.split_text(content)
        
        for chunk in chunks:
            # Extract section/clause if present in chunk
            section_match = re.search(r"(Section \d+:[^\n]+)", chunk)
            clause_match = re.search(r"(Clause \d+\.\d+:[^\n]+)", chunk)
            
            meta_section = section_match.group(1) if section_match else "Unknown Section"
            meta_clause = clause_match.group(1) if clause_match else "Unknown Clause"
            
            # Additional heuristic: if not in chunk, maybe previous ones had it?
            # For this simple prototype, relying purely on chunk contents or doing regex split manually is safer.
            
            docs.append({
                "text": chunk,
                "metadata": {
                    "source": doc_name,
                    "section": meta_section,
                    "clause": meta_clause
                }
            })
            
    # Compute embeddings
    print(f"Loading embedding model... Processing {len(docs)} chunks.")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    
    collection = get_chroma_collection()
    
    documents = [d["text"] for d in docs]
    metadatas = [d["metadata"] for d in docs]
    ids = [f"id_{i}" for i in range(len(docs))]
    
    embeddings = embedder.encode(documents).tolist()
    
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    print("Ingestion complete.")

def query_system(user_query, document_filter=None, topic_filter=None):
    print("Loading query subsystem...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    collection = get_chroma_collection()
    
    query_embedding = embedder.encode([user_query]).tolist()
    
    where_clause = {}
    if document_filter:
        where_clause["source"] = {"$eq": document_filter}
    
    # Chroma where clause
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3,
        where=where_clause if where_clause else None
    )
    
    if not results["documents"] or not results["documents"][0]:
        print("No relevant clauses found.")
        return
        
    retrieved_texts = results["documents"][0]
    retrieved_metadatas = results["metadatas"][0]
    
    # Incase topic filter is used, manually filter the retrieved texts (simple logic)
    if topic_filter:
        filtered_texts = []
        filtered_metas = []
        for text, meta in zip(retrieved_texts, retrieved_metadatas):
            if topic_filter.lower() in text.lower() or topic_filter.lower() in meta["section"].lower() or topic_filter.lower() in meta["clause"].lower():
                filtered_texts.append(text)
                filtered_metas.append(meta)
        retrieved_texts = filtered_texts
        retrieved_metadatas = filtered_metas

    if not retrieved_texts:
        print("No clauses match your specific topic filter.")
        return

    context = "\n".join(retrieved_texts)
    
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    print("Loading LLM for ELI5 simplification (this might take a moment without GPU)...")
    tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
    model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
    
    # Constructing prompt for ELI5
    prompt = f"Simplify the following legal text for a 5 year old. Context: {context} Question: {user_query}. Answer simply:"
    
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=150)
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print("\n" + "="*50)
    print("🤖 FINE PRINT DECODER:")
    print("="*50)
    print(f"Question: {user_query}")
    if document_filter: print(f"Applies to: {document_filter}")
    print("\n📝 ELI5 Answer:")
    print(answer)
    print("\n⚖️  Source Attribution:")
    for meta in retrieved_metadatas:
        print(f"  - Document: {meta['source']}")
        print(f"    {meta['section']}")
        if meta['clause'] != "Unknown Clause":
            print(f"    {meta['clause']}")
    print("="*50)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fine Print Decoder - RAG System")
    parser.add_argument("action", choices=["ingest", "query"], help="Action to perform")
    parser.add_argument("--query", type=str, help="Question to ask")
    parser.add_argument("--filter-doc", type=str, help="Filter by document name (e.g. Titan_Secure_Health_Insurance_Policy.txt)")
    parser.add_argument("--filter-topic", type=str, help="Smart filtering keyword (e.g. coverage, penalties, exclusions)")
    
    args = parser.parse_args()
    
    if args.action == "ingest":
        ingest_documents()
    elif args.action == "query":
        if not args.query:
            print("Please provide a --query!")
        else:
            query_system(args.query, args.filter_doc, args.filter_topic)

