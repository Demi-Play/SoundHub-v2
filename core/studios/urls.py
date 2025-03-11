from django.urls import path
from .views import StudioListCreateView, StudioRetrieveUpdateView, StudioVerificationView

urlpatterns = [
    path('', StudioListCreateView.as_view(), name='studio-list-create'),
    path('<int:pk>/', StudioRetrieveUpdateView.as_view(), name='studio-retrieve-update'),
    path('verification/', StudioVerificationView.as_view(), name='studio-verification'),
]