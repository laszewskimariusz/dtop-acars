"""
Official smartCARS 3 API URL Configuration
Based on invernyx/smartcars-3-phpvms7-api official module
URL Structure: /api/smartcars/
"""

from django.urls import path, re_path
from . import smartcars_api

app_name = 'smartcars'

urlpatterns = [
    # Main handler endpoint - supports both GET and POST
    # Official URL: /api/smartcars/
    re_path(r'^$', smartcars_api.handler, name='handler'),
    re_path(r'^/$', smartcars_api.handler, name='handler_slash'),
    
    # Authentication endpoints
    path('login', smartcars_api.login, name='login'),
    path('login/', smartcars_api.login, name='login_slash'),
    
    # User info endpoint
    path('user', smartcars_api.user, name='user'),
    path('user/', smartcars_api.user, name='user_slash'),
    
    # Data endpoints
    path('schedules', smartcars_api.schedules, name='schedules'),
    path('schedules/', smartcars_api.schedules, name='schedules_slash'),
    
    path('aircraft', smartcars_api.aircraft, name='aircraft'),
    path('aircraft/', smartcars_api.aircraft, name='aircraft_slash'),
    
    path('airports', smartcars_api.airports, name='airports'),
    path('airports/', smartcars_api.airports, name='airports_slash'),
    
    # Flight operations
    path('bid', smartcars_api.bid, name='bid'),
    path('bid/', smartcars_api.bid, name='bid_slash'),
    
    # ACARS data endpoints
    path('position', smartcars_api.position, name='position'),
    path('position/', smartcars_api.position, name='position_slash'),
    
    path('pirep', smartcars_api.pirep, name='pirep'),
    path('pirep/', smartcars_api.pirep, name='pirep_slash'),
] 