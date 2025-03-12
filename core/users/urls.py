from django.urls import path
from .views import register, user_login, logout_view, profile, get_users

urlpatterns = [
    path('register', register, name='register'),
    path('login', user_login, name='login'),
    path('logout', logout_view, name='logout'),
    path('profile', profile, name='profile'),
    path('', get_users, name='get_users'),
]