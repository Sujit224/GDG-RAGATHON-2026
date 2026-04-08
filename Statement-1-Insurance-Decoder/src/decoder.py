import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Setup Environment
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(current_dir, "..", ".env"))

def get_insurance_answer(query):
    # 2. Initialize Embeddings and Load Vector Store
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    persist_dir = os.path.join(current_dir, "..", "chroma_db")
    
    vector_db = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    
    # 3. Setup the LLM (Gemini 1.5 Pro is best for complex policy logic)
    # Using the explicit 8B Flash model to bypass 404s and 429s
    # Using the Lite model to bypass the 429 Quota 'limit: 0' error
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-flash-lite-latest", 
        temperature=0.3,
        max_retries=2
    )

    # 4. Craft the Prompt (The "ELI5" and "Citations" Requirement)
    system_prompt = (
        "You are the 'Titan Secure' Insurance Assistant. Your goal is to explain "
        "complex policy details in very simple, easy-to-understand language (ELI5). "
        "\n\n"
        "RULES:\n"
        "1. Use only the provided context to answer.\n"
        "2. If you don't know the answer, say you don't know.\n"
        "3. BONUS: You MUST mention the Page Number where you found the information.\n"
        "\n\n"
        "Context: {context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 5. Create the RAG Chain
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 6. Get the Result
    response = rag_chain.invoke({"input": query})
    return response["answer"]

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🛡️ Welcome to the Titan Secure Insurance Assistant!")
    print("Type 'exit' or 'quit' to end the session.")
    print("="*50)

    while True:
        # 1. Take user input
        user_query = input("\nYour Question: ")
        
        # 2. Check if they want to leave
        if user_query.lower() in ['exit', 'quit']:
            print("Closing the Assistant. Goodbye!")
            break
            
        # Ignore empty questions
        if not user_query.strip():
            continue
            
        # 3. Get the answer
        print("Searching policy documents... 🔍")
        try:
            answer = get_insurance_answer(user_query)
            print("-" * 40)
            print(f"Assistant:\n{answer}")
            print("-" * 40)
        except Exception as e:
            print(f"\nError: {e}")