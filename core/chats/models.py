# models.py
from django.db import models
from users.models import User

class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    studio = models.ForeignKey('studios.Studio', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Project(models.Model):
    PROJECT_TYPES = (
        ('album', 'Альбом'),
        ('single', 'Сингл'),
        ('ep', 'EP')
    )
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=PROJECT_TYPES)
    title = models.CharField(max_length=255)
    is_completed = models.BooleanField(default=False)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    files = models.ManyToManyField('File')
    created_at = models.DateTimeField(auto_now_add=True)

class File(models.Model):
    FILE_TYPES = (
        ('audio', 'Аудио'),
        ('video', 'Видео'),
        ('image', 'Изображение'),
        ('other', 'Другое')
    )
    file = models.FileField(upload_to='project_files/')
    type = models.CharField(max_length=10, choices=FILE_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)