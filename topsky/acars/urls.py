from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, 
    acars_dashboard, 
    smartcars_webhook,
    smartcars_auth_login,
    smartcars_user_info,
    smartcars_basic_data,
    smartcars_schedules
)

router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

urlpatterns = [
    path('', acars_dashboard, name='acars_dashboard'),
    path('webhook/', smartcars_webhook, name='smartcars_webhook'),
    path('webhook', smartcars_webhook, name='smartcars_webhook_no_slash'),  # For apps that don't handle redirects
    
    # SmartCARS API endpoints (matching phpVMS structure)
    path('login', smartcars_auth_login, name='smartcars_login'),  # POST /login (not /auth/login!)
    path('user', smartcars_user_info, name='smartcars_user'),     # GET /user
    path('schedules', smartcars_schedules, name='smartcars_schedules'),  # GET /schedules
    path('aircraft', smartcars_basic_data, name='smartcars_aircraft'),   # GET /aircraft  
    path('airports', smartcars_basic_data, name='smartcars_airports'),   # GET /airports
    
    # Django Rest Framework API
    path('api/', include(router.urls)),
] 