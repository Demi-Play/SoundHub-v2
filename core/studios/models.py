# models.py
from django.db import models
from users.models import User

class Studio(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='owned_studios', on_delete=models.CASCADE)
    workers = models.ManyToManyField(User, related_name='work_studios')
    description = models.TextField()
    address = models.TextField()
    equipment_list = models.JSONField(default=list)
    pricing = models.JSONField(default=dict)  # Формат: {"service_type": price}
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2)  # Комиссия студии

class StudioVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    documents = models.FileField(upload_to='verification/')
    status = models.CharField(max_length=20, choices=[('pending', 'На проверке'), ('approved', 'Одобрено'), ('rejected', 'Отклонено')])