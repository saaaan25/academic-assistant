from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='api_register'),
    path('chat-free/', views.chat_free, name = 'api_chat_free'),
    path('chat/', views.chat, name = 'api_chat'),
]