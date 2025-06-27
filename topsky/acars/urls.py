from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, 
    acars_dashboard, 
    smartcars_webhook,
    smartcars_auth_login,
    smartcars_user_info,
    smartcars_basic_data
)

router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

urlpatterns = [
    path('', acars_dashboard, name='acars_dashboard'),
    path('webhook/', smartcars_webhook, name='smartcars_webhook'),
    path('webhook', smartcars_webhook, name='smartcars_webhook_no_slash'),  # For apps that don't handle redirects
    
    # SmartCARS API endpoints
    path('auth/login', smartcars_auth_login, name='smartcars_auth_login'),
    path('user', smartcars_user_info, name='smartcars_user_info'),
    path('data', smartcars_basic_data, name='smartcars_basic_data'),
    
    path('api/', include(router.urls)),
] 