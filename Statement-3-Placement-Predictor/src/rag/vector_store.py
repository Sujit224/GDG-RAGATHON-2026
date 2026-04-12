from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

def load_vectorstore():
    return Chroma(persist_directory="db", embedding_function=OpenAIEmbeddings())