from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    studio_list_create_view, 
    studio_retrieve_update_view, 
    studio_verification_view, 
    studio_statistics_view,
    studio_projects_view,
    studio_create_project_view,
    studio_complete_project_view,
    studios_list_view,
    create_studio_request_view,
    StudioOwnerViewSet
)

router = DefaultRouter()
router.register(r'my-studios', StudioOwnerViewSet, basename='studio-owner')

urlpatterns = [
    # Публичные URL
    path('all/', studios_list_view, name='studios_list'),
    path('request/<int:studio_id>/', create_studio_request_view, name='create_studio_request'),
    
    # URL для владельцев студий
    path('', studio_list_create_view, name='studio_list'),
    path('<int:studio_id>/', studio_retrieve_update_view, name='studio_detail'),
    path('<int:studio_id>/statistics/', studio_statistics_view, name='studio_statistics'),
    path('<int:studio_id>/projects/', studio_projects_view, name='studio_projects'),
    path('<int:studio_id>/projects/create/', studio_create_project_view, name='studio_create_project'),
    path('<int:studio_id>/projects/complete/', studio_complete_project_view, name='studio_complete_project'),
    path('verification/', studio_verification_view, name='studio_verification'),
    path('api/', include(router.urls)),
]