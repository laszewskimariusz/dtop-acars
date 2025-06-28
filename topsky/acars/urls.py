from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, ping, bulk_create_messages,
    smartcars_handler, smartcars_login, smartcars_user, smartcars_basic_endpoint
)

# Router dla ViewSets
router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

app_name = 'acars'

urlpatterns = [
    # Główny endpoint smartCARS - tylko dokładnie /api/ (musi być PIERWSZY)
    re_path(r'^api/$', smartcars_handler, name='smartcars_handler'),
    
    # Legacy endpoints dla kompatybilności z smartCARS (konkretne ścieżki)
    path('api/login/', smartcars_login, name='smartcars_login'),
    path('api/user/', smartcars_user, name='smartcars_user'),
    path('api/schedules/', smartcars_basic_endpoint, {'endpoint_name': 'schedules'}, name='smartcars_schedules'),
    path('api/aircraft/', smartcars_basic_endpoint, {'endpoint_name': 'aircraft'}, name='smartcars_aircraft'),
    path('api/airports/', smartcars_basic_endpoint, {'endpoint_name': 'airports'}, name='smartcars_airports'),
    
    # Dodatkowe endpointy
    path('api/ping/', ping, name='ping'),
    path('api/bulk-create/', bulk_create_messages, name='bulk_create'),
    path('api/messages/bulk/', bulk_create_messages, name='bulk_create_alias'),
    
    # Nowe API endpoints dla wiadomości ACARS (REST) - router
    path('api/', include(router.urls)),
] 