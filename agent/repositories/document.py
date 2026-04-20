from ..models import Document

def save_document(title, doc_name, local_path):
    # Guardado único de documentos
    doc, created_at = Document.objects.get_or_create(
        doc_name=doc_name,
        defaults={'title': title, 'local_path': local_path}
    )
    return doc