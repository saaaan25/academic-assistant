from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

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