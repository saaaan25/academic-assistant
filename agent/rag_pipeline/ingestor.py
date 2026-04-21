import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from ..repositories.document import save_document
from .config import *
from .pdf_resolver import resolve_pdf

def index_document(route, title):
    doc_name = os.path.basename(route)
    
    # Guardar documento en db
    save_document(title, doc_name, route)
    
    # Fragmentar contenido de documentos
    fragments = resolve_pdf(route, doc_name)
    
    # Generar vectores de los fragmentos
    embeddings = HuggingFaceEmbeddings(model_name = EMBEDDING_MODEL_NAME)

    # Guardar en chromadb
    Chroma.from_documents(
        fragments,
        embeddings, 
        persist_directory = VECTOR_DB_PATH
    )
    
    print(f"'{title}' saved in chroma database")


if __name__ == "__main__":
    DIR_ROUTE = os.path.join(BASE_DIR, "data", "docs")
    
    # Verificar argumentos
    if len(sys.argv) < 3:
        print("There are missing arguments")
        print("Uso correcto: python ingestor.py <archivo.pdf> <'Nombre del Documento'>")
        sys.exit(1)
    
    # Obtener argumentos
    pdf_name = sys.argv[1]
    pdf_metadata = sys.argv[2]
    
    # Unir nombre de pdf con ruta base para buscar el documento
    pdf_route = os.path.join(DIR_ROUTE, pdf_name)
    
    # Ejecutar ingesta si existe el archivo
    if os.path.exists(pdf_route):
        index_document(pdf_route, pdf_metadata)
    else:
        print(f"PDF not found")
        print(f"Searched route: {pdf_route}")