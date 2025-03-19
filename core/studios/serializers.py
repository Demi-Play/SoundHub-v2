from rest_framework import serializers
from users.models import User
from .models import Studio, StudioVerification, StudioStatistics

class StudioVerificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudioVerification
        fields = ['documents', 'status']
        read_only_fields = ['status']

class StudioSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(
        user_type='studio_owner', 
        is_verified=True))
    workers = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.filter(user_type='studio_worker', is_verified=True))
    pricing = serializers.JSONField()
    equipment_list = serializers.JSONField()

    class Meta:
        model = Studio
        fields = ['id', 'name', 'owner', 'workers', 'description', 'address', 'equipment_list', 'pricing', 'commission_percent']
        read_only_fields = ['owner']

    def validate(self, data):
        user = self.context['request'].user
        if not hasattr(user, 'studioverification') or user.studioverification.status != 'approved':
            raise serializers.ValidationError("Studio verification required")
        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class StudioStatisticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudioStatistics
        fields = ['total_projects', 'completed_projects', 'total_revenue', 'average_rating', 'last_updated']
        read_only_fields = fields