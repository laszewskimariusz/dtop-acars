from django.urls import path
from . import views

app_name = 'acars'

urlpatterns = [
    # Main SmartCARS API endpoint - this is what goes in SmartCARS Central
    path('', views.api_info, name='api_info'),
    
    # Authentication endpoints
    path('login', views.login, name='login'),
    path('pilot', views.pilot_info, name='pilot_info'),
    path('data', views.data_info, name='data_info'),
    
    # Test endpoint
    path('test', views.test_auth, name='test_auth'),
] 