from django.contrib import admin
from .models import Document, ChatSession, Message, Citation

# Agregar modelos al panel de admin
admin.site.register(Document)
admin.site.register(ChatSession)
admin.site.register(Message)
admin.site.register(Citation)
