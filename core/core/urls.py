from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


schema_view = get_schema_view(
    openapi.Info(
        title="SoundHub-v2 API",
        default_version='v1',
        description="API documentation for SoundHub-v2",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# core/urls.py
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse

@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': 'su523cce349sseggggg523gghkh476ggggrsg532sr56747'})


urlpatterns = [
    # Главные маршруты вашего проекта
    path('admin/', admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/studios/', include('studios.urls')),
    path('api/payments/', include('payments.urls')),
    path('api/chats/', include('chats.urls')),
    path('api/ratings/', include('ratings.urls')),

    # Маршруты для документации
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('get-csrf-token/', get_csrf_token),
    
]

# Для разработки: обслуживание медиа-файлов
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)