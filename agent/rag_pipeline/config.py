import os
from dotenv import load_dotenv

load_dotenv()

# API KEY DEL MODELO LL
LLM_API_KEY = os.getenv("LLM_API_KEY")


# RUTAS
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VECTOR_DB_PATH = os.path.join(BASE_DIR, "chroma_db")


# MODELOS A UTILIZAR
LLM_MODEL_NAME = "llama3-8b-8192" 
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# VARIABLES PARA RAG
CHUNK_SIZE = 1500      
CHUNK_OVERLAP = 200    
TOP_K_RESULTS = 4