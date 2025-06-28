from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, 
    acars_dashboard, 
    smartcars_webhook,
    smartcars_handler,
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
    
    # SmartCARS API main handler (for compatibility check)
    path('api/', smartcars_handler, name='smartcars_handler'),  # GET /acars/api/ - main handler info
    path('api', smartcars_handler, name='smartcars_handler_no_slash'),  # without trailing slash
    
    # SmartCARS API endpoints (matching phpVMS structure)
    path('api/login', smartcars_auth_login, name='smartcars_login'),  # POST /acars/api/login
    path('api/user', smartcars_user_info, name='smartcars_user'),     # GET /acars/api/user
    path('api/schedules', smartcars_schedules, name='smartcars_schedules'),  # GET /acars/api/schedules
    path('api/aircraft', smartcars_basic_data, name='smartcars_aircraft'),   # GET /acars/api/aircraft  
    path('api/airports', smartcars_basic_data, name='smartcars_airports'),   # GET /acars/api/airports
    
    # Legacy endpoints (for backward compatibility)
    path('login', smartcars_auth_login, name='smartcars_login_legacy'),  
    path('user', smartcars_user_info, name='smartcars_user_legacy'),     
    path('schedules', smartcars_schedules, name='smartcars_schedules_legacy'),  
    path('aircraft', smartcars_basic_data, name='smartcars_aircraft_legacy'),   
    path('airports', smartcars_basic_data, name='smartcars_airports_legacy'),   
    
    # Django Rest Framework API
    path('drf/', include(router.urls)),  # Moved to avoid conflicts
] 