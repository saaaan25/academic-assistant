
from ..models.chat_session import ChatSession

def get_or_create_session(user, id_session=None):
    if id_session:
        return ChatSession.objects.get(id=id_session, user=user)
    return ChatSession.objects.create(user=user)