from django.urls import path
from .views import (
    register_view,
    user_login,
    logout_view,
    profile,
    verify_role_view,
    musician_dashboard,
    studio_owner_dashboard,
    studio_worker_dashboard,
    update_profile
)

urlpatterns = [
    path('register', register_view, name='register'),
    path('login', user_login, name='login'),
    path('logout', logout_view, name='logout'),
    path('profile', profile, name='profile'),
    path('profile/update', update_profile, name='profile_update'),
    path('verify-role/', verify_role_view, name='verify_role'),
    path('dashboard/musician/', musician_dashboard, name='musician_dashboard'),
    path('dashboard/studio-owner/', studio_owner_dashboard, name='studio_owner_dashboard'),
    path('dashboard/studio-worker/', studio_worker_dashboard, name='studio_worker_dashboard'),
]