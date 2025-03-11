from django.contrib import admin
from .models import User, UserProfile
from studios.models import StudioVerification

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(StudioVerification)