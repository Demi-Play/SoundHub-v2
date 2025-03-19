from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import StudioForm, StudioVerificationForm
from .models import Studio, StudioVerification, StudioStatistics
from .serializers import StudioSerializer, StudioVerificationSerializer, StudioStatisticsSerializer
from chats.models import Chat, Project
from chats.serializers import ChatSerializer, ProjectSerializer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages

class IsStudioOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'studio_owner' and request.user.is_verified

@login_required
def studio_list_create_view(request):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    studios = Studio.objects.filter(owner=request.user)
    has_studio = studios.exists()

    if request.method == 'POST':
        if has_studio:
            messages.error(request, 'У вас уже есть студия. Создание дополнительных студий не разрешено.')
            return redirect('studio_list')
            
        form = StudioForm(request.POST, request.FILES)
        if form.is_valid():
            studio = form.save(commit=False)
            studio.owner = request.user
            studio.save()
            messages.success(request, 'Студия успешно создана!')
            return redirect('studio_list')
    else:
        form = StudioForm()

    return render(request, 'studio_list.html', {
        'studios': studios,
        'form': form,
        'has_studio': has_studio
    })

@login_required
def studio_retrieve_update_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)

    if request.method == 'POST':
        form = StudioForm(request.POST, request.FILES, instance=studio)
        if form.is_valid():
            form.save()
            return redirect('studio_list')
    else:
        form = StudioForm(instance=studio)

    return render(request, 'studio_detail.html', {'studio': studio, 'form': form})

@login_required
def studio_verification_view(request):
    if request.user.user_type != 'studio_owner':
        return render(request, 'errors/403.html', status=403)

    verification, created = StudioVerification.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = StudioVerificationForm(request.POST, request.FILES, instance=verification)
        if form.is_valid():
            form.save()
            return redirect('studio_verification')
    else:
        form = StudioVerificationForm(instance=verification)

    return render(request, 'studio_verification.html', {'verification': verification, 'form': form})

class StudioOwnerViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStudioOwner]
    serializer_class = StudioSerializer

    def get_queryset(self):
        return Studio.objects.filter(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        studio = self.get_object()
        stats, created = StudioStatistics.objects.get_or_create(studio=studio)
        stats.update_statistics()
        return Response(StudioStatisticsSerializer(stats).data)

    @action(detail=True, methods=['get'])
    def project_requests(self, request, pk=None):
        studio = self.get_object()
        chats = Chat.objects.filter(studio=studio, project__isnull=True)
        return Response(ChatSerializer(chats, many=True).data)

    @action(detail=True, methods=['post'])
    def create_project(self, request, pk=None):
        studio = self.get_object()
        chat_id = request.data.get('chat_id')
        project_type = request.data.get('type')
        title = request.data.get('title')

        if not all([chat_id, project_type, title]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        chat = get_object_or_404(Chat, id=chat_id, studio=studio)
        if chat.project:
            return Response({'error': 'Chat already has a project'}, status=status.HTTP_400_BAD_REQUEST)

        project = Project.objects.create(
            chat=chat,
            type=project_type,
            title=title
        )

        return Response(ProjectSerializer(project).data)

    @action(detail=True, methods=['post'])
    def complete_project(self, request, pk=None):
        studio = self.get_object()
        project_id = request.data.get('project_id')

        if not project_id:
            return Response({'error': 'Project ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        project = get_object_or_404(Project, id=project_id, chat__studio=studio)
        if project.is_completed:
            return Response({'error': 'Project is already completed'}, status=status.HTTP_400_BAD_REQUEST)

        project.is_completed = True
        project.save()

        # Update studio statistics
        stats, _ = StudioStatistics.objects.get_or_create(studio=studio)
        stats.update_statistics()

        return Response(ProjectSerializer(project).data)

@receiver(post_save, sender=Studio)
def create_studio_statistics(sender, instance, created, **kwargs):
    if created:
        StudioStatistics.objects.create(studio=instance)

@login_required
def studio_statistics_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    stats, created = StudioStatistics.objects.get_or_create(studio=studio)
    stats.update_statistics()

    return render(request, 'studio_statistics.html', {
        'studio': studio,
        'statistics': stats
    })

@login_required
def studio_projects_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    
    # Получаем заявки на проекты (чаты без проектов)
    project_requests = Chat.objects.filter(studio=studio, project__isnull=True)
    
    # Получаем активные проекты
    active_projects = Project.objects.filter(
        chat__studio=studio,
        is_completed=False
    ).select_related('chat')

    return render(request, 'studio_projects.html', {
        'studio': studio,
        'project_requests': project_requests,
        'active_projects': active_projects
    })

@login_required
def studio_create_project_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
        chat_id = request.POST.get('chat_id')
        project_type = request.POST.get('type')
        title = request.POST.get('title')

        if not all([chat_id, project_type, title]):
            return redirect('studio_projects', studio_id=studio_id)

        chat = get_object_or_404(Chat, id=chat_id, studio=studio)
        if not chat.project:
            Project.objects.create(
                chat=chat,
                type=project_type,
                title=title
            )

    return redirect('studio_projects', studio_id=studio_id)

@login_required
def studio_complete_project_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
        project_id = request.POST.get('project_id')

        if project_id:
            project = get_object_or_404(Project, id=project_id, chat__studio=studio)
            if not project.is_completed:
                project.is_completed = True
                project.save()

                # Обновляем статистику
                stats, _ = StudioStatistics.objects.get_or_create(studio=studio)
                stats.update_statistics()

    return redirect('studio_projects', studio_id=studio_id)

def is_musician(user):
    return user.is_authenticated and user.user_type == 'musician'

def studios_list_view(request):
    studios = Studio.objects.all()
    return render(request, 'studios_list.html', {'studios': studios})

@login_required
@user_passes_test(is_musician)
def create_studio_request_view(request, studio_id):
    if request.method == 'POST':
        studio = get_object_or_404(Studio, id=studio_id)
        project_type = request.POST.get('project_type')
        title = request.POST.get('title')
        description = request.POST.get('description')

        if not all([project_type, title, description]):
            messages.error(request, 'Пожалуйста, заполните все поля.')
            return redirect('studios_list')

        # Создаем чат для общения
        chat = Chat.objects.create(studio=studio)
        chat.participants.add(request.user, studio.owner)
        chat.save()

        # Создаем проект
        project = Project.objects.create(
            chat=chat,
            type=project_type,
            title=title
        )

        messages.success(request, 'Заявка успешно создана!')
        return redirect('studios_list')

    return redirect('studios_list')

@login_required
def studio_schedule(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)
    
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    return render(request, 'studios/studio_schedule.html', {'studio': studio})

@login_required
def studio_workers(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)
    
    
    
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    return render(request, 'studios/studio_workers.html', {'studio': studio})

@login_required
def studio_finances(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)
    
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    return render(request, 'studios/studio_finances.html', {'studio': studio})

@login_required
def studio_reviews(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)
    
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    return render(request, 'studios/studio_reviews.html', {'studio': studio})

@login_required
def worker_schedule(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/worker_schedule.html')

@login_required
def worker_tasks(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/worker_tasks.html')

@login_required
def worker_skills(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/worker_skills.html')

@login_required
def worker_portfolio(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/worker_portfolio.html')

@login_required
def task_detail(request, task_id):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'studios/task_detail.html', {'task': task})

@login_required
def request_time_off(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/request_time_off.html')