from ..rag_pipeline.retriever import search_fragments
from ..rag_pipeline.generator import generate_response

def process_question(user_question):
    # Obtener conexto relevante de los reglamentos
    fragments = search_fragments(user_question)
    
    # Generar respuesta usando el contexto obtenido
    response = generate_response(user_question, fragments)
    
    # Registrar las fuentes utilizadas para generar la respuesta
    sources = []
    for f in fragments:
        doc_name = f.metadata.get('source', 'Documento Desconocido')
        sources.append({"documento": doc_name})
        
    return response, sources