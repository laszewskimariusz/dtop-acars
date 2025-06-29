"""
URL configuration for topsky project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.http import HttpResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('auth/', include('accounts.urls')),
    
    # SmartCARS 3 API - Main endpoint for SmartCARS Central
    # This is the URL you put in SmartCARS Central as "Script URL"
    # Both with and without trailing slash for SmartCARS compatibility
    path('api/smartcars/', include(('acars.urls', 'acars'), namespace='smartcars_main')),
    path('api/smartcars', include(('acars.urls', 'acars'), namespace='smartcars_alt')),
    
    # Alternative ACARS endpoints
    path('acars/api/', include(('acars.urls', 'acars'), namespace='acars_main')),
    path('acars/api', include(('acars.urls', 'acars'), namespace='acars_alt')),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Django's password reset email templates URLs (without namespace)
    path('auth/password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # Landing page (home)
    path('', include('landing.urls')),
]

# Add django_browser_reload URLs in development - disabled for Railway debugging
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
