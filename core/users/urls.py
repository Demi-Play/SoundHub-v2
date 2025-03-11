from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserViewSet

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('', UserViewSet.as_view()),
]