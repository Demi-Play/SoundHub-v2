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
    request_time_off,
    studio_detail_view,
    add_worker_to_chat,
    accept_worker_request,
    reject_worker_request,
    request_to_join_studio,
    available_studios_view,
    dismiss_worker,
    studio_project_detail_view
)

router = DefaultRouter()
router.register(r'my-studios', StudioOwnerViewSet, basename='studio')

app_name = 'studios'

urlpatterns = [
    # Публичные URL
    path('all/', studios_list_view, name='studios_list'),
    path('<int:studio_id>/', studio_detail_view, name='studio_detail'),
    path('request/<int:studio_id>/', create_studio_request_view, name='create_studio_request'),
    
    # URL для владельцев студий
    path('', studios_list_view, name='studio_list'),
    path('my/', studio_list_create_view, name='studio_list'),
    path('create/', create_studio_request_view, name='create_studio'),
    path('verify/', studio_verification_view, name='studio_verification'),
    path('<int:studio_id>/edit/', studio_retrieve_update_view, name='studio_retrieve_update'),
    path('<int:studio_id>/statistics/', studio_statistics_view, name='studio_statistics'),
    path('<int:studio_id>/projects/', studio_projects_view, name='studio_projects'),
    path('<int:studio_id>/projects/create/', studio_create_project_view, name='studio_create_project'),
    path('<int:studio_id>/projects/<int:project_id>/', studio_project_detail_view, name='studio_project_detail'),
    path('<int:studio_id>/projects/<int:project_id>/complete/', studio_complete_project_view, name='studio_complete_project'),
    path('<int:studio_id>/schedule/', studio_schedule, name='studio_schedule'),
    path('<int:studio_id>/workers/', studio_workers, name='studio_workers'),
    path('<int:studio_id>/workers/<int:worker_id>/dismiss/', dismiss_worker, name='dismiss_worker'),
    path('<int:studio_id>/workers/<int:worker_id>/add-to-chat/', add_worker_to_chat, name='add_worker_to_chat'),
    path('worker-requests/<int:request_id>/accept/', accept_worker_request, name='accept_worker_request'),
    path('worker-requests/<int:request_id>/reject/', reject_worker_request, name='reject_worker_request'),
    path('<int:studio_id>/finances/', studio_finances, name='studio_finances'),
    path('<int:studio_id>/reviews/', studio_reviews, name='studio_reviews'),
    path('worker/schedule/', worker_schedule, name='worker_schedule'),
    path('worker/tasks/', worker_tasks, name='worker_tasks'),
    path('worker/skills/', worker_skills, name='worker_skills'),
    path('worker/portfolio/', worker_portfolio, name='worker_portfolio'),
    path('worker/tasks/<int:task_id>/', task_detail, name='task_detail'),
    path('worker/request-time-off/', request_time_off, name='request_time_off'),
    path('available/', available_studios_view, name='available_studios'),
    path('request-to-join/<int:studio_id>/', request_to_join_studio, name='request_to_join_studio'),
    path('api/', include(router.urls)),
]