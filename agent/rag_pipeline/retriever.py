from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from . import config

def search_fragments(question):
    # Búsqueda en chromadb
    embeddings = HuggingFaceEmbeddings(model_name=config.EMBEDDING_MODEL_NAME)
    
    vectorstore = Chroma(
        persist_directory=config.VECTOR_DB_PATH, 
        embedding_function=embeddings
    )
    
    # Retornar los fragmentos más similares a la pregunta
    return vectorstore.similarity_search(question, k = config.TOP_K_RESULTS)