from rest_framework import serializers
from ..models import Document, ChatSession, Message, Citation


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'title', 'doc_name', 'created_at']

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSession
        fields = ['id', 'chat_name', 'created_at']

class CitationSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)
    class Meta:
        model = Citation
        fields = ['page', 'fragment_text', 'document']

class MessageSerializer(serializers.ModelSerializer):
    citations = CitationSerializer(many=True, read_only=True)
    
    class Meta:
        model = Message
        fields = ['id', 'question', 'answer', 'created_at', 'citations']