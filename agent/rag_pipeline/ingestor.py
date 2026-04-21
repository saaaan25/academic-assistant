import os
import sys
import django
from functools import lru_cache

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from ..repositories.document import save_document
from .config import *
from .pdf_resolver import resolve_pdf

@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)


def index_document(route, title):
    doc_name = os.path.basename(route)

    # Fragmentar contenido de documentos
    fragments = resolve_pdf(route, doc_name)

    # Generar vectores de los fragmentos
    embeddings = get_embeddings()

    # Guardar en chromadb
    Chroma.from_documents(
        fragments,
        embeddings,
        persist_directory=VECTOR_DB_PATH
    )

    # Guardar documento en db solo si la ingesta termino correctamente
    save_document(title, doc_name, route)

    print(f"'{title}' saved in chroma database")


if __name__ == "__main__":
    DIR_ROUTE = DOCS_DIR
    
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
