from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from studios.models import Studio
from .models import Wallet

class PaymentTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='payer',
            password='payer123',
            user_type='musician',
            is_verified=True
        )
        self.studio_owner = User.objects.create_user(
            username='owner',
            password='owner123',
            user_type='studio_owner',
            is_verified=True
        )
        self.studio = Studio.objects.create(
            owner=self.studio_owner,
            name='Test Studio',
            commission_percent=10
        )
        Wallet.objects.create(user=self.user, balance=1000)
        self.client.force_authenticate(user=self.user)

    def test_deposit(self):
        response = self.client.post('/api/payments/deposit/', {'amount': 500})
        self.assertEqual(response.status_code, 200)
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 1500)

    def test_payment(self):
        response = self.client.post('/api/payments/pay/', {
            'studio_id': self.studio.id,
            'amount': 300,
            'service_type': 'recording'
        })
        self.assertEqual(response.status_code, 201)
        self.user.wallet.refresh_from_db()
        self.assertEqual(self.user.wallet.balance, 700)
        self.studio_owner.wallet.refresh_from_db()
        self.assertEqual(self.studio_owner.wallet.balance, 300)