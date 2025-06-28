"""
Topsky Plugin URL Configuration
Custom smartCARS 3 implementation for Topsky Virtual Airlines
URL Structure: /api/topskyplugin/
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import topsky_smartcars_login, ACARSMessageViewSet

# Router dla REST API messages
router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='topskyplugin-messages')

app_name = 'topsky_plugin'

urlpatterns = [
    # Login endpoint dla smartCARS plugin
    path('login', topsky_smartcars_login, name='login'),
    
    # Messages API endpoints (GET/POST/PUT/DELETE)
    path('', include(router.urls)),
] 