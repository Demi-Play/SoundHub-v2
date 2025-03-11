from django.test import TestCase
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from users.models import User
from studios.models import Studio
from .models import Chat, Message

class ChatTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='musician',
            password='music123',
            user_type='musician',
            is_verified=True
        )
        self.owner = User.objects.create_user(
            username='owner',
            password='owner123',
            user_type='studio_owner',
            is_verified=True
        )
        self.studio = Studio.objects.create(
            owner=self.owner,
            name='Test Studio',
            commission_percent=10
        )
        self.client.force_authenticate(user=self.user)

    def test_create_chat(self):
        response = self.client.post('/api/chats/create/', 
                                   {'studio_id': self.studio.id})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Chat.objects.filter(studio=self.studio).exists())

    def test_send_message(self):
        chat = Chat.objects.create(studio=self.studio)
        chat.participants.add(self.user, self.owner)
        file = SimpleUploadedFile("test.txt", b"content")
        response = self.client.post('/api/chats/messages/send/', 
                                   {'chat_id': chat.id, 'text': 'Hello', 'files': [file]})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().files.count(), 1)