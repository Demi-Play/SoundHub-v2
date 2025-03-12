from rest_framework import generics, permissions
from .models import Studio, StudioVerification
from .serializers import StudioSerializer, StudioVerificationSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import StudioForm, StudioVerificationForm

class IsStudioOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.user_type == 'studio_owner' and request.user.is_verified

@login_required
def studio_list_create_view(request):
    if request.user.user_type != 'studio_owner' or not request.user.is_verified:
        return render(request, 'errors/403.html', status=403)

    if request.method == 'POST':
        form = StudioForm(request.POST, request.FILES)
        if form.is_valid():
            studio = form.save(commit=False)
            studio.owner = request.user
            studio.save()
            return redirect('studio_list')
    else:
        form = StudioForm()

    studios = Studio.objects.filter(owner=request.user)
    return render(request, 'studio_list.html', {'studios': studios, 'form': form})

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