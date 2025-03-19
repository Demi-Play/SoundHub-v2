from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer, LoginSerializer
from .models import User, UserProfile
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
# class UserViewSet(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     def get(self, request):
#         return Response(self.serializer_class(self.get_queryset(), many=True).data)
    
@login_required
def get_users(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('verify_role')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
    user = User.objects.get(username=request.user.username)
    if request.method == 'POST':
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)

        profile.bio = request.POST.get('bio', '')
        profile.genres = request.POST.get('genres', '').split(', ')
        profile.instruments = request.POST.get('instruments', '').split(', ')
        profile.social_links = eval(request.POST.get('social_links', '{}'))  # Осторожно с eval
        profile.save()
        return redirect('profile')
    return render(request, 'profile.html', {'user': user})

@login_required
def verify_role_view(request):
    if request.user.is_authenticated:
        if request.user.user_type:
            messages.info(request, 'Вы уже выбрали роль.')
            if request.user.user_type == 'musician':
                return redirect('musician_dashboard')
            elif request.user.user_type == 'studio_owner':
                return redirect('studio_owner_dashboard')
            else:
                return redirect('studio_worker_dashboard')
        
        if request.method == 'POST':
            role = request.POST.get('role')
            if role in dict(User.USER_TYPES):
                request.user.user_type = role
                request.user.save()
                messages.success(request, f'Роль успешно установлена: {dict(User.USER_TYPES)[role]}')
                if role == 'musician':
                    return redirect('musician_dashboard')
                elif role == 'studio_owner':
                    return redirect('studio_owner_dashboard')
                else:
                    return redirect('studio_worker_dashboard')
            else:
                messages.error(request, 'Неверная роль.')
    
    return render(request, 'users/verify_role.html')

@login_required
def musician_dashboard(request):
    if request.user.user_type != 'musician':
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('profile')
    return render(request, 'users/dashboards/musician_dashboard.html')

@login_required
def studio_owner_dashboard(request):
    if request.user.user_type != 'studio_owner':
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('profile')
    return render(request, 'users/dashboards/studio_owner_dashboard.html')

@login_required
def studio_worker_dashboard(request):
    if request.user.user_type != 'studio_worker':
        messages.error(request, 'У вас нет доступа к этой странице.')
        return redirect('profile')
    return render(request, 'users/dashboards/studio_worker_dashboard.html')

# def update_profile(request):
#     if request.method == 'POST':
#         try:
#             profile = request.user.userprofile
#         except UserProfile.DoesNotExist:
#             profile = UserProfile.objects.create(user=request.user)

#         profile.bio = request.POST.get('bio', '')
#         profile.genres = request.POST.get('genres', '').split(', ')
#         profile.instruments = request.POST.get('instruments', '').split(', ')
#         profile.social_links = eval(request.POST.get('social_links', '{}'))  # Осторожно с eval
#         profile.save()
#         return redirect('profile')
#     return redirect('profile')