from ..rag_pipeline.retriever import search_fragments
from ..rag_pipeline.generator import generate_response, generate_response_with_history
from ..repositories.chat_session import get_or_create_session
from ..repositories.chat import save_interaction

# Endpoint sin autenticación
def process_question_free(user_question):
    # Obtener conexto relevante de los reglamentos
    fragments = search_fragments(user_question)
    
    # Generar respuesta usando el contexto obtenido
    response = generate_response(user_question, fragments)
    
    # Registrar las fuentes utilizadas para generar la respuesta
    sources = []
    for f in fragments:
        doc_name = f.metadata.get('source', 'Documento Desconocido')
        sources.append({"document": doc_name})
        
    return response, sources


# Endpoint con autenticación
def process_question_user(user, question, id_session=None):
    # Recuperar contexto relevante de los documentos
    fragments = search_fragments(question)
    response = generate_response(question, fragments)
    
    # Crear o recuperar sesión de chat
    session = get_or_create_session(user, id_session)
    save_interaction(session, question, response, fragments)
    
    # Formato a enviar al frontend
    sources = []
    for f in fragments:
        sources.append({
            "document": f.metadata.get('source'),
            "page": f.metadata.get('page', 0) + 1
        })
        
    return response, sources, session.id


# Endpoint con historial
def process_question(user, question, id_session=None):
    session = get_or_create_session(user, id_session)
    
    # Obtener mensajes anteriores del chat
    mensajes_anteriores = session.messages.all().order_by('created_at')
    
    history = ""
    for msg in mensajes_anteriores:
        history += f"User: {msg.question}\nAssistant: {msg.answer}\n\n"
        
    # Recuperar contexto relevante
    fragments = search_fragments(question)
    
    # Enviar historial
    response = generate_response_with_history(question, fragments, history)
    
    # Guardar interacción
    save_interaction(session, question, response, fragments)
    
    # Formato a enviar al frontend
    sources = []
    for f in fragments:
        sources.append({
            "document": f.metadata.get('source'),
            "page": f.metadata.get('page', 0) + 1
        })
        
    return response, sources, session.id