from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Rating, BonusPoints
from .serializers import RatingSerializer, BonusPointsSerializer
from chats.models import Project
from users.models import User

class RatingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = Project.objects.filter(id=project_id).first()
        if not project:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user != project.chat.studio.owner:
            return Response({'error': 'Only studio owners can rate'}, status=status.HTTP_403_FORBIDDEN)
        
        score = request.data.get('score')
        comment = request.data.get('comment')

        rating = Rating.objects.create(
            project=project,
            rated_by=request.user,
            score=score,
            comment=comment
        )

        # Начисление бонусов
        if score >= 4:
            bonus, created = BonusPoints.objects.get_or_create(user=project.chat.studio.owner)
            bonus.points += 10
            bonus.save()
        elif score <= 2:
            # Логирование для админа
            pass

        return Response(RatingSerializer(rating).data)

class BonusPointsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bonus = BonusPoints.objects.filter(user=request.user).first()
        serializer = BonusPointsSerializer(bonus)
        return Response(serializer.data)