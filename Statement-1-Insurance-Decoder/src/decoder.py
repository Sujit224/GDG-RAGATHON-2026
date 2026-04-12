import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# Setup Environment
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, "..", ".env"))

def get_insurance_answer(query):
    # Initialize Embeddings and Load Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    persist_dir = os.path.join(current_dir, "..", "chroma_db")
    
    vector_db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    # Setup the LLM (Lite model to avoid Quota issues)
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-lite-latest", 
        temperature=0.3,
        max_retries=2
    )

    # The upgraded prompt for Bonus Points (+5)
    system_prompt = (
        "You are a helpful Legal and Insurance Assistant. Your goal is to explain "
        "complex policy details in very simple, easy-to-understand language (ELI5). "
        "\n\n"
        "RULES:\n"
        "1. Use only the provided context to answer. Do not make things up.\n"
        "2. If you don't know the answer, say you don't know.\n"
        "3. CITATION: You must cite your source at the end of your answer. Try to include the "
        "Section, Clause number, and Page Number. If the Section/Clause is not visible in the text, "
        "just cite the Document Name and Page Number.\n"
        "\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create the RAG Chain
    retriever = vector_db.as_retriever(search_kwargs={"k": 10}) # Increased K slightly for better context
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # Get the Result
    response = rag_chain.invoke({"input": query})
    return response["answer"]

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🛡️ Welcome to the Multi-Document Policy Assistant!")
    print("Type 'exit' or 'quit' to end the session.")
    print("="*60)

    while True:
        user_query = input("\nYour Question: ")
        
        if user_query.lower() in ['exit', 'quit']:
            print("Closing the Assistant. Goodbye!")
            break
            
        if not user_query.strip():
            continue
            
        print("Searching policy documents... 🔍")
        try:
            answer = get_insurance_answer(user_query)
            print("-" * 50)
            print(f"Assistant:\n{answer}")
            print("-" * 50)
        except Exception as e:
            print(f"\nError: {e}")