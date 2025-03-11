from django.test import TestCase
from rest_framework.test import APIClient
from users.models import User
from .models import Studio

class StudioTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_user(
            username='owner',
            password='owner123',
            user_type='studio_owner',
            is_verified=True
        )
        self.client.force_authenticate(user=self.owner)

    # В studios/tests.py добавляем обязательные поля:
    def test_create_studio(self):
        data = {
            'name': 'Test Studio',
            'description': 'Test description',
            'address': 'Test address',
            'equipment_list': ['Microphone'],  # Список вместо строки
            'pricing': {'recording': 100},     # Словарь вместо строки
            'commission_percent': 10
        }
        response = self.client.post('/api/studios/', data, format='json')
        self.assertEqual(response.status_code, 201)

    # В studios/tests.py исправляем данные PATCH-запроса:
    # studios/tests.py
    def test_update_studio(self):
        studio = Studio.objects.create(
            owner=self.owner,
            name='Old Name',
            description='Old desc',
            address='Old address',
            equipment_list=['Old equipment'],
            pricing={'old': 50},
            commission_percent=5
        )
        response = self.client.patch(f'/api/studios/{studio.id}/', 
                                    {
                                        'name': 'New Name',
                                        'equipment_list': ['New equipment'],
                                        'pricing': {'new': 100}
                                    }, format='json')
        self.assertEqual(response.status_code, 200)