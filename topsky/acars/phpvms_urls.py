"""
Official smartCARS 3 API URLs - 1:1 Compatible with phpVMS
URL Structure: /api/smartcars/
Based on: https://github.com/invernyx/smartcars-3-phpvms7-api
"""

from django.urls import path, re_path
from django.http import HttpResponsePermanentRedirect
from .phpvms_api import (
    api_handler, api_login, api_user, api_schedules, 
    api_aircraft, api_airports, api_bid, api_position, api_pirep
)

app_name = 'phpvms_smartcars'

# Redirect function for URLs without trailing slash
def redirect_to_slash(request):
    """Redirect smartCARS URLs to include trailing slash"""
    path_with_slash = request.path_info + '/'
    return HttpResponsePermanentRedirect(path_with_slash)

urlpatterns = [
    # Main handler endpoint - Official smartCARS 3 entry point
    # GET/POST/HEAD /api/smartcars/
    re_path(r'^$', api_handler, name='handler'),
    re_path(r'^/$', api_handler, name='handler_slash'),
    
    # Authentication endpoint - Official smartCARS 3 login
    # POST /api/smartcars/login
    path('login/', api_login, name='login'),
    path('login', api_login, name='login_no_slash'),  # Handle both variants
    
    # User info endpoint - Official smartCARS 3 user info
    # GET /api/smartcars/user?session=api_key
    path('user/', api_user, name='user'),
    path('user', api_user, name='user_no_slash'),
    
    # Data endpoints - Official smartCARS 3 data
    # GET /api/smartcars/schedules?session=api_key
    path('schedules/', api_schedules, name='schedules'),
    path('schedules', api_schedules, name='schedules_no_slash'),
    
    # GET /api/smartcars/aircraft?session=api_key
    path('aircraft/', api_aircraft, name='aircraft'),
    path('aircraft', api_aircraft, name='aircraft_no_slash'),
    
    # GET /api/smartcars/airports?session=api_key
    path('airports/', api_airports, name='airports'),
    path('airports', api_airports, name='airports_no_slash'),
    
    # Flight operations - Official smartCARS 3 flight ops
    # POST /api/smartcars/bid
    path('bid/', api_bid, name='bid'),
    path('bid', api_bid, name='bid_no_slash'),
    
    # ACARS data endpoints - Official smartCARS 3 ACARS
    # POST /api/smartcars/position
    path('position/', api_position, name='position'),
    path('position', api_position, name='position_no_slash'),
    
    # POST /api/smartcars/pirep
    path('pirep/', api_pirep, name='pirep'),
    path('pirep', api_pirep, name='pirep_no_slash'),
] 