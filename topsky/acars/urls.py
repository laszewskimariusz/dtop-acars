from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from .views import (
    ACARSMessageViewSet, ping, bulk_create_messages,
    smartcars_handler, smartcars_login, smartcars_user, smartcars_basic_endpoint,
    debug_requests
)
from . import smartcars_api


# Router dla ViewSets
router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

app_name = 'acars'

urlpatterns = [
    # Główny endpoint smartCARS - obsługa obu wariantów (z i bez trailing slash)
    re_path(r'^api/$', smartcars_handler, name='smartcars_handler'),
    re_path(r'^api$', smartcars_handler, name='smartcars_handler_no_slash'),
    
    # Official SmartCARS 3 API endpoints (from smartcars_api.py)
    path('api/smartcars/', smartcars_api.handler, name='smartcars3_handler'),
    path('api/smartcars', smartcars_api.handler, name='smartcars3_handler_no_slash'),
    
    path('api/smartcars/login/', smartcars_api.acars_login, name='smartcars3_login'),
    path('api/smartcars/login', smartcars_api.acars_login, name='smartcars3_login_no_slash'),
    
    path('api/smartcars/user/', smartcars_api.user, name='smartcars3_user'),
    path('api/smartcars/user', smartcars_api.user, name='smartcars3_user_no_slash'),
    
    path('api/smartcars/schedules/', smartcars_api.schedules, name='smartcars3_schedules'),
    path('api/smartcars/schedules', smartcars_api.schedules, name='smartcars3_schedules_no_slash'),
    
    path('api/smartcars/aircraft/', smartcars_api.aircraft, name='smartcars3_aircraft'),
    path('api/smartcars/aircraft', smartcars_api.aircraft, name='smartcars3_aircraft_no_slash'),
    
    path('api/smartcars/airports/', smartcars_api.airports, name='smartcars3_airports'),
    path('api/smartcars/airports', smartcars_api.airports, name='smartcars3_airports_no_slash'),
    
    path('api/smartcars/bid/', smartcars_api.bid, name='smartcars3_bid'),
    path('api/smartcars/bid', smartcars_api.bid, name='smartcars3_bid_no_slash'),
    
    path('api/smartcars/position/', smartcars_api.position, name='smartcars3_position'),
    path('api/smartcars/position', smartcars_api.position, name='smartcars3_position_no_slash'),
    
    path('api/smartcars/pirep/', smartcars_api.pirep, name='smartcars3_pirep'),
    path('api/smartcars/pirep', smartcars_api.pirep, name='smartcars3_pirep_no_slash'),

    # Legacy endpoints dla kompatybilności z smartCARS (konkretne ścieżki)
    path('api/login/', smartcars_login, name='smartcars_login'),
    path('api/login', smartcars_login, name='smartcars_login_no_slash'),
    path('api/user/', smartcars_user, name='smartcars_user'),
    path('api/user', smartcars_user, name='smartcars_user_no_slash'),
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
    path('api/debug/', debug_requests, name='debug_requests'),
    
    # Nowe API endpoints dla wiadomości ACARS (REST) - router
    path('api/', include(router.urls)),
] 