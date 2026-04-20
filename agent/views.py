from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .services.chat_service import process_question

@api_view(['POST'])
@permission_classes([AllowAny]) 
def chat_endpoint(request):
    question = request.data.get('question')
    
    if not question:
        return Response({"error": "There is no question"}, status = 400)
    
    return Response({
        "status": "Success",
        "message": f"Question: '{question}', (model to implement)"
    })

@api_view(['POST'])
@permission_classes([AllowAny]) 
def chat(request):
    question = request.data.get('question')
    
    if not question:
        return Response({"error": "There is no question"}, status = 400)
    
    # Utilizar el servicio para procesar la pregunta y generar una respuesta
    try:
        response, sources = process_question(question)
        
        return Response({
            "pregunta": question,
            "respuesta": response,
            "fuentes": sources
        })
    except Exception as e:
        return Response({"error": f"Cannot process LLM: {str(e)}"}, status = 500)