from django.test import TestCase
from rest_framework.test import APIClient
from chats.models import Project
from users.models import User
from chats.models import Chat
from studios.models import Studio



class RatingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
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
        self.chat = Chat.objects.create(studio=self.studio)
        self.chat.participants.add(self.owner)
        self.project = Project.objects.create(
            chat=self.chat,
            type='single',
            title='Test Project'
        )
        self.client.force_authenticate(user=self.owner)

    def test_rating(self):
        response = self.client.post(f'/api/ratings/projects/{self.project.id}/', 
                                   {'score': 5, 'comment': 'Great work!'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.owner.bonuspoints.points, 10)