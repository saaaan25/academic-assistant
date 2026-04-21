from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterUserSerializer
from .services.chat_service import process_question, process_question_user
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterUserSerializer(data=request.data)
    
    # Validar información ingresada
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User registered successfully",
            "user": serializer.data
        }, status = status.HTTP_201_CREATED)
        
    # Si la información no es válida, retornar errores
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny]) 
def chat_free(request):
    question = request.data.get('question')
    
    if not question:
        return Response({"error": "There is no question"}, status = 400)
    
    # Utilizar el servicio para procesar la pregunta y generar una respuesta
    try:
        response, sources = process_question_user(question)
        
        return Response({
            "question": question,
            "answer": response,
            "sources": sources
        })
    except Exception as e:
        return Response({"error": f"Cannot process LLM: {str(e)}"}, status = 500)
    

# Ruta protegida, implementación con usuarios
@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def chat(request):
    question = request.data.get('question')
    id_session = request.data.get('id_session')
    
    if not question:
        return Response({"error": "There is no question"}, status =400)
    
    try:
        # Recibe al usuario autenticado desde el token
        answer, sources, id_session = process_question(
            user = request.user, 
            question = question, 
            id_session = id_session
        )
        # Retorna con sesión de chat
        return Response({
            "id_session": id_session,
            "question": question,
            "answer": answer,
            "sources": sources
        })
    
    except Exception as e:
        return Response({"error": str(e)}, status = 500)