# models.py
from django.db import models
from users.models import User
from chats.models import Project

class Rating(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    rated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BonusPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)