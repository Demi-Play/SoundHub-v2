from rest_framework import serializers
from .models import Chat, Project, Message, File
from users.serializers import UserSerializer
from studios.serializers import StudioSerializer

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'file', 'type', 'uploaded_at']

class MessageSerializer(serializers.ModelSerializer):
    files = FileSerializer(many=True, read_only=True)
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'chat', 'sender', 'text', 'files', 'created_at']
        read_only_fields = ['sender', 'chat']

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'chat', 'type', 'title', 'is_completed']
        read_only_fields = ['chat']

class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    studio = StudioSerializer(read_only=True)
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'participants', 'studio', 'created_at', 'project']