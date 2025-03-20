# models.py
from django.db import models
from users.models import User
from django.conf import settings

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

class StudioStatistics(models.Model):
    studio = models.OneToOneField(Studio, on_delete=models.CASCADE, related_name='statistics')
    total_projects = models.IntegerField(default=0)
    completed_projects = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    last_updated = models.DateTimeField(auto_now=True)

    def update_statistics(self):
        from chats.models import Project
        from ratings.models import Rating
        
        projects = Project.objects.filter(chat__studio=self.studio)
        self.total_projects = projects.count()
        self.completed_projects = projects.filter(status='completed').count()
        
        # Calculate total revenue from completed projects
        completed_projects = projects.filter(status='completed')
        self.total_revenue = sum(project.payment.amount for project in completed_projects if hasattr(project, 'payment'))
        
        # Calculate average rating
        ratings = Rating.objects.filter(project__chat__studio=self.studio)
        if ratings.exists():
            self.average_rating = ratings.aggregate(models.Avg('score'))['score__avg']
        else:
            self.average_rating = 0
            
        self.save()

class StudioWorkerRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена')
    ]

    studio = models.ForeignKey(Studio, on_delete=models.CASCADE, related_name='worker_requests')
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='studio_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    message = models.TextField(blank=True)

    class Meta:
        unique_together = ['studio', 'worker']

    def __str__(self):
        return f'Заявка {self.worker.get_full_name()} в студию {self.studio.name}'