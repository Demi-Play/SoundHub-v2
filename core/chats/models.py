# models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from users.models import User

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='client_projects', default=0)
    studio = models.ForeignKey('studios.Studio', on_delete=models.CASCADE, related_name='studio_projects', default=0)
    status = models.CharField(max_length=20, choices=[
        ('new', 'Новый'),
        ('in_progress', 'В работе'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен')
    ], default='new')

    def __str__(self):
        return self.title

class Chat(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name='chat', null=True, blank=True)
    studio = models.ForeignKey('studios.Studio', on_delete=models.CASCADE, related_name='chats', null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_last_message(self):
        return self.messages.order_by('-created_at').first()

    def get_unread_messages_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()

    def __str__(self):
        return f'Чат проекта: {self.project.title if self.project else "Без проекта"}'

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'Сообщение от {self.sender.username} в {self.chat}'

class File(models.Model):
    FILE_TYPES = [
        ('audio', 'Аудио'),
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('document', 'Документ')
    ]

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files', default='')
    file = models.FileField(upload_to='chat_files/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default=FILE_TYPES[3][0])
    filename = models.CharField(max_length=255, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField(help_text='Размер файла в байтах', default=0)

    def save(self, *args, **kwargs):
        if not self.filename:
            self.filename = self.file.name
        if not self.size or self.size == 0:
            self.size = self.file.size if self.file else 0
        if not self.file_type:
            # Определяем тип файла по расширению
            ext = self.filename.split('.')[-1].lower()
            if ext in ['mp3', 'wav', 'ogg']:
                self.file_type = 'audio'
            elif ext in ['jpg', 'jpeg', 'png', 'gif']:
                self.file_type = 'image'
            elif ext in ['mp4', 'avi', 'mov']:
                self.file_type = 'video'
            else:
                self.file_type = 'document'
        super().save(*args, **kwargs)

    def get_preview_url(self):
        if self.file_type == 'image':
            return self.file.url
        elif self.file_type == 'video':
            # Здесь можно добавить генерацию превью для видео
            return '/static/images/video-preview.png'
        elif self.file_type == 'audio':
            # Здесь можно добавить генерацию превью для аудио
            return '/static/images/audio-preview.png'
        else:
            return '/static/images/document-preview.png'

    def __str__(self):
        return self.filename