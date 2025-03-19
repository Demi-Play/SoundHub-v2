from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404, render, redirect
from django.db import transaction
from studios.models import Studio
from .models import Chat, Project, Message, File
from .serializers import ChatSerializer, ProjectSerializer, MessageSerializer, FileSerializer
from users.models import User
from payments.models import Payment, Transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST
from django.conf import settings
import json

# pylint: disable=no-member

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        studio_id = request.data.get('studio_id')
        studio = Studio.objects.filter(id=studio_id).first()
        if not studio:
            return Response({'error': 'Studio not found'}, status=status.HTTP_404_NOT_FOUND)
        
        chat = Chat.objects.create(studio=studio)
        chat.participants.add(request.user, studio.owner)
        chat.save()

        return Response(ChatSerializer(chat).data)

class MessageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id)
        if request.user not in chat.participants.all():
            return Response({"error": "Not a chat participant"}, status=403)
            
        messages = Message.objects.filter(chat=chat).order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request):
        chat_id = request.data.get('chat_id')
        text = request.data.get('text')
        files = request.FILES.getlist('files')
        
        chat = get_object_or_404(Chat, id=chat_id)
        if request.user not in chat.participants.all():
            return Response({"error": "Not a chat participant"}, status=403)
            
        message = Message.objects.create(chat=chat, sender=request.user, text=text)
        for file in files:
            File.objects.create(message=message, file=file, type=file.content_type.split('/')[0])
            
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProjectCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, project_id):
        project = get_object_or_404(Project, id=project_id)
        chat = project.chat
        
        if request.user not in [chat.studio.owner, *chat.participants.exclude(id=chat.studio.owner.id)]:
            return Response({"error": "Only project participants can complete"}, status=403)
            
        project.is_completed = True
        project.save()
        
        # Логика распределения средств
        if project.payment and not project.payment.is_processed:
            studio = project.payment.studio
            total = project.payment.amount
            commission = total * (studio.commission_percent / 100)
            worker_share = (total - commission) / studio.workers.count()
            
            with transaction.atomic():
                for worker in studio.workers.all():
                    Transaction.objects.create(
                        wallet=worker.wallet,
                        amount=worker_share,
                        type='commission',
                        payment=project.payment
                    )
                project.payment.is_processed = True
                project.payment.save()
                
        return Response({"status": "Project completed successfully"})

@login_required
def project_chat(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Проверяем права доступа
    if request.user != project.client and request.user not in project.studio.workers.all():
        raise PermissionDenied
    
    chat, created = Chat.objects.get_or_create(project=project)
    messages = chat.messages.select_related('sender').prefetch_related('files').order_by('created_at')
    
    if request.method == 'POST':
        text = request.POST.get('message')
        files = request.FILES.getlist('files')
        
        if text or files:
            message = Message.objects.create(
                chat=chat,
                sender=request.user,
                text=text
            )
            
            for file in files:
                File.objects.create(
                    message=message,
                    file=file,
                    filename=file.name,
                    size=file.size
                )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                message_html = render_to_string('chats/message.html', {
                    'message': message,
                    'user': request.user
                })
                return JsonResponse({'message_html': message_html})
            
            return redirect('project_chat', project_id=project_id)
    
    return render(request, 'chats/chat.html', {
        'project': project,
        'chat': chat,
        'messages': messages
    })

@login_required
@require_POST
def mark_as_read(request):
    data = json.loads(request.body)
    message_id = data.get('message_id')
    message = get_object_or_404(Message, id=message_id)
    
    if request.user != message.chat.project.client and request.user not in message.chat.project.studio.workers.all():
        raise PermissionDenied
    
    message.is_read = True
    message.save()
    
    return JsonResponse({'status': 'ok'})

@login_required
def download_file(request, file_id):
    file = get_object_or_404(File, id=file_id)
    message = file.message
    
    if request.user != message.chat.project.client and request.user not in message.chat.project.studio.workers.all():
        raise PermissionDenied
    
    response = JsonResponse({
        'file_url': file.file.url,
        'filename': file.filename
    })
    
    return response