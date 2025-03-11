from rest_framework import serializers
from .models import Rating, BonusPoints
from users.serializers import UserSerializer
from chats.serializers import ProjectSerializer

class RatingSerializer(serializers.ModelSerializer):
    rated_by = UserSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'project', 'rated_by', 'score', 'comment', 'created_at']

class BonusPointsSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = BonusPoints
        fields = ['user', 'points']