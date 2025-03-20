from django.urls import path
from . import views

app_name = 'chats'

urlpatterns = [
    # Отметка сообщений как прочитанных
    path('mark-as-read/', views.mark_messages_as_read, name='mark_as_read'),
    
    # Создание чата между пользователем и студией
    path('chats/create/', views.ChatView.as_view(), name='chat-create'),
    
    # Отправка сообщения в чат
    path('messages/send/', views.MessageView.as_view(), name='message-send'),
    
    # Завершение проекта
    path('projects/<int:project_id>/complete/', views.ProjectCompleteView.as_view(), name='project-complete'),
    
    # Получение всех сообщений чата
    path('chats/<int:chat_id>/messages/', views.MessageView.as_view(), name='chat-messages'),
    
    path('project/<int:project_id>/', views.project_chat, name='project_chat'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
]