from rest_framework import generics, permissions
from .models import Studio, StudioVerification
from .serializers import StudioSerializer, StudioVerificationSerializer


class IsStudioOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'studio_owner' and request.user.is_verified

class StudioListCreateView(generics.ListCreateAPIView):
    serializer_class = StudioSerializer
    permission_classes = [IsStudioOwner]

    def get_queryset(self):
        return Studio.objects.filter(owner=self.request.user)

class StudioRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = StudioSerializer
    permission_classes = [IsStudioOwner]

    def get_queryset(self):
        return Studio.objects.filter(owner=self.request.user)

class StudioVerificationView(generics.RetrieveUpdateAPIView):
    serializer_class = StudioVerificationSerializer
    permission_classes = [IsStudioOwner]

    def get_object(self):
        return StudioVerification.objects.get(user=self.request.user)