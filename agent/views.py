from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegisterUserSerializer
from .services.chat_service import process_question, process_question_user, process_question_free
from rest_framework.permissions import IsAuthenticated
from .models import Document, ChatSession, Message, Citation
from .serializers import DocumentSerializer, SessionSerializer, MessageSerializer

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
        response, sources = process_question_free(question)
        
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
def chat_user(request):
    question = request.data.get('question')
    id_session = request.data.get('id_session')
    
    if not question:
        return Response({"error": "There is no question"}, status =400)
    
    try:
        # Recibe al usuario autenticado desde el token
        answer, sources, id_session = process_question_user(
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


# Obtener respuesta con historial 
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

# GET sessions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_sessions(request):
    sessions = ChatSession.objects.filter(user = request.user).order_by('-created_at')
    serializer = SessionSerializer(sessions, many = True)
    return Response(serializer.data)


# GET messages BY session
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_messages_by_session(request, id_session):
    try:
        session = ChatSession.objects.get(id = id_session, user = request.user)
        messages = Message.objects.filter(session = session).order_by('created_at')
        serializer = MessageSerializer(messages, many = True)
        return Response(serializer.data)
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found or not authorized"}, status = 404)


# GET documents
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_documents(request):
    documents = Document.objects.all()
    serializer = DocumentSerializer(documents, many = True)
    return Response(serializer.data)


# Renombrar o borrar chat
@api_view(['DELETE', 'PATCH'])
@permission_classes([IsAuthenticated])
def manage_session(request, id_session):
    try:
        session = ChatSession.objects.get(id = id_session, user = request.user)
        
        if request.method == 'DELETE':
            session.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
            
        elif request.method == 'PATCH':
            new_name = request.data.get('new_name') # Body de la petición
            if not new_name:
                return Response({"error": "You must provide a name"}, status = 400)
            session.nombre_chat = new_name
            session.save()
            return Response({"message": "Renamed", "new_name": new_name})
            
    except ChatSession.DoesNotExist:
        return Response({"error": "Session not found"}, status = 404)