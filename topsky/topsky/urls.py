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
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from acars.smartcars_api import debug_login, acars_login

urlpatterns = [
    # SmartCARS 3 Official API endpoint - CRITICAL for ACARS login - FIRST in URL list
    path('pilot/login', acars_login, name='smartcars3_pilot_login'),
    path('pilot/login/', acars_login, name='smartcars3_pilot_login_slash'),
    path('pilot-test/', acars_login, name='pilot_test'),  # Test endpoint
    
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    
    # Standard PHPvMS5 compatible endpoints for SmartCARS
    path('api/acars-login/', acars_login, name='phpvms5_acars_login'),
    path('api/acars-login', acars_login, name='phpvms5_acars_login_no_slash'),
    
    # Debug endpoint
    path('api/debug-login/', debug_login, name='debug_acars_login'),
    path('api/debug-login', debug_login, name='debug_acars_login_no_slash'), 
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # JWT Authentication endpoints (zgodnie z wymaganiami ACARS)
    path('api/auth/login/', TokenObtainPairView.as_view(), name='acars_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='acars_refresh'),
    
    # ACARS API (legacy)
    path('acars/', include('acars.urls')),
    
    # Official smartCARS 3 API (1:1 compatible with phpVMS)
    path('api/smartcars/', include('acars.phpvms_urls')),
    
    # smartCARS 3 compatibility - handle URL without trailing slash
    re_path(r'^api/smartcars$', include('acars.phpvms_urls')),
    
    # Topsky Plugin API - Custom smartCARS implementation
    path('api/topskyplugin/', include('acars.topsky_plugin_urls')),
    
    # ACARS Bridge Plugin API
    path('api/', include('acars.acars_bridge_urls')),
    
    # URL aliases for Django's password reset email templates (without namespace)
    path('auth/password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    
    path('', include('landing.urls')),
]

# Add django_browser_reload URLs in development
if settings.DEBUG:
    urlpatterns += [
        path('__reload__/', include('django_browser_reload.urls')),
    ]
