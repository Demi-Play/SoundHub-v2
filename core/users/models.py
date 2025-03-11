# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    USER_TYPES = (
        ('musician', 'Музыкант'),
        ('studio_owner', 'Владелец студии'),
        ('studio_worker', 'Работник студии')
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/')
    bio = models.TextField(blank=True)
    social_links = models.JSONField(default=dict)
    # Для музыкантов
    instruments = models.JSONField(default=list)
    genres = models.JSONField(default=list)
    # Для студий
    studio = models.ForeignKey('studios.Studio', null=True, blank=True, on_delete=models.SET_NULL)