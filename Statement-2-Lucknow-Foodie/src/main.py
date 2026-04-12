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
    persist_directory= "Foodie_DB",
    embedding_function=embedding_model
)

retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 6 
    }
)

model  = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    temperature= 0.4,
    max_new_tokens=512
)

llm = ChatHuggingFace(llm = model)

from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are the ultimate IIIT Lucknow Foodie Guide, a friendly and knowledgeable local expert helping students find the perfect place to eat.

Your objective is to recommend restaurants to the user based STRICTLY on the provided context. 

CRITICAL INSTRUCTIONS:
1. Grounded Recommendations: You will be provided with details of restaurants that have already passed the user's budget and dietary filters. Recommend ONLY from this list. Do not invent restaurants or prices.
2. Highlight the Best Parts: Use the 'Signature Dishes', 'Vibe', and 'Reviews' from the context to write a personalized, appetizing recommendation. Tell them WHY they should go there.
3. Empty Context Fallback: If the context is empty, it means no restaurants matched their strict filters. Reply warmly: "I couldn't find any places matching those exact filters close by! Try increasing your budget or expanding your search area."
4. Tone: Keep it casual, energetic, and helpful—like a senior giving advice to a hungry junior after a long day of classes.

Context of matching restaurants:
{context}
"""
        ),
        (
            "human",
            """User's Request: {question}"""
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
    