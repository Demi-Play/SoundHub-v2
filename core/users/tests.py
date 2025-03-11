from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()

class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'user_type': 'musician'
        }
        self.admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )

    # В users/tests.py добавляем обязательные поля профиля:
    def test_registration(self):
        data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com',
            'user_type': 'musician',
            'profile': {
                'avatar': 'avatar.jpg',
                'bio': 'Test bio'
            }
        }
        response = self.client.post('/api/users/register/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login(self):
        User.objects.create_user(**self.user_data)
        response = self.client.post('/api/token/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_profile_access(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        response = self.client.get('/api/users/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')

    def test_logout(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)
        
        # Получаем токены
        response = self.client.post('/api/token/')
        refresh_token = response.data['refresh']
        
        # Выходим
        response = self.client.post('/api/users/logout/', 
                                {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)