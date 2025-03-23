from django.contrib import admin
from .models import User, UserProfile
from studios.models import (
    Studio, StudioVerification, StudioStatistics,
    StudioWorkerRequest
)
from chats.models import Project
from payments.models import Wallet, Payment
from ratings.models import Rating

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Studio)
admin.site.register(StudioVerification)
admin.site.register(StudioStatistics)
admin.site.register(StudioWorkerRequest)
admin.site.register(Project)
admin.site.register(Wallet)
admin.site.register(Payment)
admin.site.register(Rating)