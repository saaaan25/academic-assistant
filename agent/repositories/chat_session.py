
from ..models.chat_session import ChatSession

def get_or_create_session(user, id_sesion=None):
    if id_sesion:
        return ChatSession.objects.get(id=id_sesion, user=user)
    return ChatSession.objects.create(user=user)