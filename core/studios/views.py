from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import StudioForm, StudioVerificationForm
from .models import Studio, StudioVerification, StudioStatistics, StudioWorkerRequest
from .serializers import StudioSerializer, StudioVerificationSerializer, StudioStatisticsSerializer
from chats.models import Chat, Project
from chats.serializers import ChatSerializer, ProjectSerializer
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

User = get_user_model()

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
            messages.error(request, 'У вас уже есть студия. Создание дополнительных студий с этой подпиской не доступно.')
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
            return redirect('studios:studio_list')
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
        if project.status == 'completed':
            return Response({'error': 'Project is already completed'}, status=status.HTTP_400_BAD_REQUEST)

        project.status = 'completed'
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
    studio = get_object_or_404(Studio, id=studio_id)
    
    # Если пользователь - владелец студии, перенаправляем на специальное представление
    if request.user.user_type == 'studio_owner' and request.user.is_verified:
        return studio_owner_projects_view(request, studio_id)
    
    # Для музыкантов показываем только их проекты
    user_projects = Project.objects.filter(
        studio=studio,
        client=request.user
    ).select_related('chat')
    
    return render(request, 'studios/studio_projects.html', {
        'studio': studio,
        'user_projects': user_projects
    })

@login_required
def studio_owner_projects_view(request, studio_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    
    # Получаем все проекты студии
    projects = Project.objects.filter(studio=studio).select_related('chat', 'client')
    
    # Получаем работников студии
    workers = studio.workers.all()
    
    return render(request, 'studios/studio_owner_projects.html', {
        'studio': studio,
        'projects': projects,
        'workers': workers
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
            if project.status != 'completed':
                project.status = 'completed'
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
            return redirect('studios:studios_list')

        try:
            # Создаем проект
            project = Project.objects.create(
                title=title,
                description=description,
                client=request.user,
                studio=studio,
                status='new'
            )

            # Создаем чат
            chat = Chat.objects.create(
                project=project,
                studio=studio
            )
            
            # Добавляем участников
            chat.participants.add(request.user, studio.owner)

            messages.success(request, 'Заявка успешно создана!')
            return redirect('chats:project_chat', project_id=project.id)

        except Exception as e:
            messages.error(request, f'Произошла ошибка при создании заявки: {str(e)}')
            return redirect('studios:studios_list')

    return redirect('studios:studios_list')

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
    
    # Получаем текущих работников
    current_workers = studio.workers.all()
    
    # Получаем заявки на вступление
    worker_requests = StudioWorkerRequest.objects.filter(
        studio=studio,
        status='pending'
    ).select_related('worker')
    
    return render(request, 'studios/studio_workers.html', {
        'studio': studio,
        'current_workers': current_workers,
        'worker_requests': worker_requests
    })

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
    if request.user.user_type != 'studio_worker' or request.user.user_type != 'studio_owner':
        return render(request, 'errors/403.html', status=403)
    
    if request.user.user_type == 'studio_worker':
        tasks = Project.objects.filter(client=request.user)
    else:
        tasks = Project.objects.filter(studio=request.user.owned_studios.first())
    
    return render(request, 'studios/worker_tasks.html', {'tasks': tasks})

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
    if request.user.user_type != 'studio_worker' or request.user.user_type != 'studio_owner':
        return render(request, 'errors/403.html', status=403)
    
    task = get_object_or_404(Task, id=task_id)
    return render(request, 'studios/task_detail.html', {'task': task})

@login_required
def request_time_off(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    return render(request, 'studios/request_time_off.html')

def studio_detail_view(request, studio_id):
    studio = get_object_or_404(Studio.objects.select_related('owner'), id=studio_id)
    return render(request, 'studios/studio_details.html', {
        'studio': studio
    })

@login_required
@require_POST
def add_worker_to_chat(request, project_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    project = get_object_or_404(Project, id=project_id)
    studio = project.studio
    
    if request.user != studio.owner:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    worker_id = request.POST.get('worker_id')
    if not worker_id:
        return JsonResponse({'error': 'Worker ID is required'}, status=400)
    
    worker = get_object_or_404(studio.workers, id=worker_id)
    chat = project.chat
    
    # Добавляем работника в чат
    chat.participants.add(worker)
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def accept_worker_request(request, request_id):
    if request.user.user_type != 'studio_owner':
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    worker_request = get_object_or_404(StudioWorkerRequest, id=request_id)
    studio = worker_request.studio
    
    if request.user != studio.owner:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Проверяем, что работник еще не в студии
    if worker_request.worker in studio.workers.all():
        return JsonResponse({'error': 'Worker is already in the studio'}, status=400)
    
    # Добавляем работника в студию
    studio.workers.add(worker_request.worker)
    worker_request.status = 'accepted'
    worker_request.save()
    
    return JsonResponse({'status': 'success'})

@login_required
@require_POST
def reject_worker_request(request, request_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    worker_request = get_object_or_404(StudioWorkerRequest, id=request_id)
    studio = worker_request.studio
    
    if request.user != studio.owner:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    worker_request.status = 'rejected'
    worker_request.save()
    
    return JsonResponse({'status': 'success'})

@login_required
def request_to_join_studio(request, studio_id):
    if request.user.user_type != 'studio_worker':
        messages.error(request, 'Только работники студии могут отправлять заявки на вступление.')
        return redirect('studios:available_studios')
    
    studio = get_object_or_404(Studio, id=studio_id)
    
    if request.method == 'POST':
        # Проверяем, не является ли пользователь уже работником студии
        if request.user in studio.workers.all():
            messages.error(request, 'Вы уже являетесь работником этой студии.')
            return redirect('studios:available_studios')
        
        # Проверяем, нет ли уже активной заявки или заявки в любом статусе
        existing_request = StudioWorkerRequest.objects.filter(
            studio=studio,
            worker=request.user
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                messages.error(request, 'У вас уже есть активная заявка на вступление в эту студию.')
            elif existing_request.status == 'accepted':
                messages.error(request, 'Вы уже были приняты в эту студию.')
            elif existing_request.status == 'rejected':
                messages.error(request, 'Ваша предыдущая заявка была отклонена.')
            return redirect('studios:available_studios')
        
        try:
            # Создаем новую заявку
            message = request.POST.get('message', '')
            worker_request = StudioWorkerRequest.objects.create(
                studio=studio,
                worker=request.user,
                message=message
            )
            
            messages.success(request, 'Заявка на вступление в студию успешно отправлена.')
        except Exception as e:
            messages.error(request, 'Произошла ошибка при отправке заявки. Пожалуйста, попробуйте позже.')
    
    return redirect('studios:available_studios')

@login_required
def available_studios_view(request):
    if request.user.user_type != 'studio_worker':
        return render(request, 'errors/403.html', status=403)
    
    # Получаем все студии, в которых пользователь еще не работает
    studios = Studio.objects.exclude(workers=request.user).select_related('owner')
    
    return render(request, 'studios/available_studios.html', {
        'studios': studios
    })

@login_required
def dismiss_worker(request, studio_id, worker_id):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)
    
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    worker = get_object_or_404(User, id=worker_id)
    
    if request.method == 'POST':
        if worker in studio.workers.all():
            studio.workers.remove(worker)
            messages.success(request, f'Сотрудник {worker.get_full_name()} успешно уволен из студии.')
        else:
            messages.error(request, 'Этот пользователь не является сотрудником студии.')
    
    return redirect('studios:studio_workers', studio_id=studio_id)

@login_required
def studio_project_detail_view(request, studio_id, project_id):
    """Детальный просмотр проекта студии"""
    studio = get_object_or_404(Studio, id=studio_id, owner=request.user)
    project = get_object_or_404(Project, id=project_id, studio=studio)
    
    context = {
        'studio': studio,
        'project': project,
        'workers': studio.workers.all(),
        'messages': project.chat.messages.all().order_by('-created_at')[:50],
    }
    
    return render(request, 'studios/studio_project_detail.html', context)