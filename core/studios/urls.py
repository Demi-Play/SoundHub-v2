from django.urls import path
from .views import studio_list_create_view, studio_retrieve_update_view, studio_verification_view

urlpatterns = [
    path('', studio_list_create_view, name='studio_list'),
    path('/<int:studio_id>', studio_retrieve_update_view, name='studio_detail'),
    path('verification', studio_verification_view, name='studio_verification'),
]