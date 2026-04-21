from django.db import models
from agent.models.message import Message
from agent.models.document import Document

class Citation(models.Model):
    message = models.ForeignKey(Message, related_name='citations', on_delete=models.CASCADE)
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    page = models.IntegerField()
    fragment_text = models.TextField()