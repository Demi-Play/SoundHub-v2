from django.urls import path
from .views import ChatView, MessageView, ProjectCompleteView

urlpatterns = [
    # Создание чата между пользователем и студией
    path('chats/create/', ChatView.as_view(), name='chat-create'),
    
    # Отправка сообщения в чат
    path('messages/send/', MessageView.as_view(), name='message-send'),
    
    # Завершение проекта
    path('projects/<int:project_id>/complete/', ProjectCompleteView.as_view(), name='project-complete'),
    
    # Получение всех сообщений чата
    path('chats/<int:chat_id>/messages/', MessageView.as_view(), name='chat-messages'),
]