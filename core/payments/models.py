# models.py
from django.db import models
from users.models import User
from studios.models import Studio

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Пополнение'),
        ('withdrawal', 'Вывод'),
        ('payment', 'Оплата'),
        ('tip', 'Чаевые'),
        ('commission', 'Комиссия')
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

class Payment(models.Model):
    studio = models.ForeignKey(Studio, on_delete=models.CASCADE)
    payer = models.ForeignKey(User, related_name='payments_made', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_type = models.CharField(max_length=50)
    is_processed = models.BooleanField(default=False)

class Tip(models.Model):
    sender = models.ForeignKey(User, related_name='tips_sent', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='tips_received', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)