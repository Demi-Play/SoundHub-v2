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
    StudioOwnerViewSet,
    studio_schedule,
    studio_workers,
    studio_finances,
    studio_reviews,
    worker_schedule,
    worker_tasks,
    worker_skills,
    worker_portfolio,
    task_detail,
    request_time_off
)

router = DefaultRouter()
router.register(r'my-studios', StudioOwnerViewSet, basename='studio')

app_name = 'studios'

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
    path('<int:studio_id>/schedule/', studio_schedule, name='studio_schedule'),
    path('<int:studio_id>/workers/', studio_workers, name='studio_workers'),
    path('<int:studio_id>/finances/', studio_finances, name='studio_finances'),
    path('<int:studio_id>/reviews/', studio_reviews, name='studio_reviews'),
    path('worker/schedule/', worker_schedule, name='worker_schedule'),
    path('worker/tasks/', worker_tasks, name='worker_tasks'),
    path('worker/skills/', worker_skills, name='worker_skills'),
    path('worker/portfolio/', worker_portfolio, name='worker_portfolio'),
    path('task/<int:task_id>/', task_detail, name='task_detail'),
    path('request-time-off/', request_time_off, name='request_time_off'),
]