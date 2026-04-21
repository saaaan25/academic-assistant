from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='api_register'),
    path('chat/', views.chat, name = 'api_chat'),
    path('chat-free/', views.chat_free, name = 'api_chat_free'),
    path('chat-user/', views.chat, name = 'api_chat_user'),

    path('sessions/', views.get_sessions, name='api_sessions'),
    path('sessions/<int:id_session>/', views.manage_session, name='api_manage_session'),
    path('sessions/<int:id_session>/messages/', views.get_messages_by_session, name='api_session_messages'),
    path('documents/', views.get_documents, name='api_documents'),
]