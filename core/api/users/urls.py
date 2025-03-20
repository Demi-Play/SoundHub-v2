from django.urls import path
from . import views

app_name = 'api_users'

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
]