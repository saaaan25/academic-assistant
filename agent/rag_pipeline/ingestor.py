from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from . import config
from .pdf_resolver import resolve_pdf

import os
import sys

def index_document(route, name):
    # Obtener fragmentos del pdf
    fragments = resolve_pdf(route, name)
    
    print(f"Generating vector for {len(fragments)} fragments")
    embeddings = HuggingFaceEmbeddings(model_name = config.EMBEDDING_MODEL_NAME)
    
    # Guardar en ChromaDB
    Chroma.from_documents(
        documents = fragments,
        embedding = embeddings,
        persist_directory = config.VECTOR_DB_PATH
    )
    print(f"'{name}' saved in chroma database")

if __name__ == "__main__":
    DIR_ROUTE = os.path.join(config.BASE_DIR, "data", "docs")
    
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