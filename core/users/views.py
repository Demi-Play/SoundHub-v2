from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .serializers import UserSerializer, RegisterSerializer, UserProfileSerializer, LoginSerializer
from .models import User, UserProfile
from django.shortcuts import render, redirect
# class UserViewSet(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     def get(self, request):
#         return Response(self.serializer_class(self.get_queryset(), many=True).data)
    
@login_required
def get_users(request):
    users = User.objects.all()
    return render(request, 'users.html', {'users': users})

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists'})
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return redirect('login')
    return render(request, 'register.html')


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
    from django.contrib.auth import logout
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