from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, ping, bulk_create_messages,
    smartcars_handler, smartcars_login, smartcars_user, smartcars_basic_endpoint,
    debug_requests
)


# Router dla ViewSets
router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

app_name = 'acars'

urlpatterns = [
    # Główny endpoint smartCARS - obsługa obu wariantów (z i bez trailing slash)
    re_path(r'^api/$', smartcars_handler, name='smartcars_handler'),
    re_path(r'^api$', smartcars_handler, name='smartcars_handler_no_slash'),  # Bez slash dla smartCARS
    
    # SmartCARS compatible paths (phpvms5/pilot/login structure)
    path('api/phpvms5/pilot/login/', smartcars_login, name='smartcars_login_phpvms5'),
    path('api/phpvms5/pilot/login', smartcars_login, name='smartcars_login_phpvms5_no_slash'),
    
    # Legacy endpoints dla kompatybilności z smartCARS (konkretne ścieżki)
    path('api/login/', smartcars_login, name='smartcars_login'),
    path('api/login', smartcars_login, name='smartcars_login_no_slash'),  # Bez slash
    path('api/user/', smartcars_user, name='smartcars_user'),
    path('api/user', smartcars_user, name='smartcars_user_no_slash'),  # Bez slash
    path('api/schedules/', smartcars_basic_endpoint, {'endpoint_name': 'schedules'}, name='smartcars_schedules'),
    path('api/schedules', smartcars_basic_endpoint, {'endpoint_name': 'schedules'}, name='smartcars_schedules_no_slash'),
    path('api/aircraft/', smartcars_basic_endpoint, {'endpoint_name': 'aircraft'}, name='smartcars_aircraft'),
    path('api/aircraft', smartcars_basic_endpoint, {'endpoint_name': 'aircraft'}, name='smartcars_aircraft_no_slash'),
    path('api/airports/', smartcars_basic_endpoint, {'endpoint_name': 'airports'}, name='smartcars_airports'),
    path('api/airports', smartcars_basic_endpoint, {'endpoint_name': 'airports'}, name='smartcars_airports_no_slash'),
    
    # Dodatkowe endpointy
    path('api/ping/', ping, name='ping'),
    path('api/bulk-create/', bulk_create_messages, name='bulk_create'),
    path('api/messages/bulk/', bulk_create_messages, name='bulk_create_alias'),
    path('api/debug/', debug_requests, name='debug_requests'),  # Panel debugowy
    
    # Nowe API endpoints dla wiadomości ACARS (REST) - router
    path('api/', include(router.urls)),
] 