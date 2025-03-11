from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import UserProfile
from studios.models import StudioVerification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'user_type', 'is_verified']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['username', 'avatar', 'bio', 'social_links', 'instruments', 'genres', 'studio']

class StudioVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudioVerification
        fields = ['documents']

class RegisterSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    verification = StudioVerificationSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'user_type', 'profile', 'verification']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        verification_data = validated_data.pop('verification', None)
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        if user.user_type in ['studio_owner', 'studio_worker']:
            if verification_data:
                StudioVerification.objects.create(user=user, **verification_data)
            else:
                raise serializers.ValidationError("Verification documents required for studio roles")
        return user
    
class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password']
