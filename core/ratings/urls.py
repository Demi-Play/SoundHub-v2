from django.urls import path
from .views import RatingView, BonusPointsView

urlpatterns = [
    path('ratings/<int:project_id>/', RatingView.as_view(), name='rating'),
    path('bonus-points/', BonusPointsView.as_view(), name='bonus-points'),
]