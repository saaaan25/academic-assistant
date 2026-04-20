from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from . import config

def resolve_pdf(route, name):
    loader = PyMuPDFLoader(route)
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = config.CHUNK_SIZE,
        chunk_overlap = config.CHUNK_OVERLAP 
    )
    
    fragments = splitter.split_documents(docs)
    
    # Inyectar nombre del documento en los metadatos
    for f in fragments:
        f.metadata["source"] = name
        
    return fragments