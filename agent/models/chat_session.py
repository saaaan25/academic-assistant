from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_name = models.CharField(max_length=100, default="Nuevo chat")
    created_at = models.DateTimeField(auto_now_add=True)