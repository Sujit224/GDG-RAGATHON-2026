from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

embedding_model = HuggingFaceEmbeddings(
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    # dimensions = 64
)

vectorstore = Chroma(
    persist_directory= "Chroma_DB",
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type = "mmr",
    search_kwargs = {
        "k" : 6,
        "fetch_k":10,
        "lambda_mult" :0.5
    }
)

model  = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    temperature= 0.01,
    max_new_tokens=512
)

llm = ChatHuggingFace(llm = model)

from langchain_core.prompts import ChatPromptTemplate

# 1. Define the strict formatting prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a precise and strictly formatted AI assistant for the TITAN SECURE health insurance policy.
Your objective is to answer the user's question based ONLY on the provided context.

CRITICAL INSTRUCTION:
You MUST format your response exactly like the examples below. Do not use conversational filler (e.g., "Based on the text...", "Hello!"). Provide the direct outcome or answer, followed by a comma, and the exact section/point citation.

FORMAT EXAMPLES:
- No, per Section III, Point 2
- 40% penalty on the claim, per Section 2.2
- No, unless in Addendum B, which is not part of Platinum, per Section III, Point 4

If the answer is not contained within the provided context, you must reply exactly with:
"Information not found in the provided policy document."
"""
        ),
        (
            "human",
            """Context:
{context}

Question:
{question}
"""
        )
    ]
)

print("Rag system created ")

print("press 0 to exit ")

while True:
    query = input("You : ")
    if query == "0":
        break 
    
    docs = retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )
    
    final_prompt = prompt.invoke({
        "context" :context,
        "question": query
    })
    
    response = llm.invoke(final_prompt)

    print(f"\n AI: {response.content}")
    