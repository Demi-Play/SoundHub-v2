from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Админка
    path('admin/', admin.site.urls),
    
    # Авторизация JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Приложения
    path('api/users/', include('users.urls')),
    path('api/studios/', include('studios.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/chats/', include('chats.urls')),
    path('api/ratings/', include('ratings.urls')),
]

# Для разработки: обслуживание медиа-файлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)