from ..models import ChatSession, Message, Citation, Document

def save_interaction(session, question, answer, used_fragments):
    # Guardar mensaje
    new_message = Message.objects.create(
        session=session,
        question=question,
        answer=answer
    )
    
    # Guardar citas utilizadas
    for frag in used_fragments:
        doc_name = frag.metadata.get('source')
        try:
            doc_db = Document.objects.get(doc_name=doc_name)
            Citation.objects.create(
                message=new_message,
                document=doc_db,
                page=frag.metadata.get('page', 0) + 1, 
                fragment_text=frag.page_content[:500] 
            )
        except Document.DoesNotExist:
            print(f"Alert: Document {doc_name} not found in the database.") 
            
    return new_message