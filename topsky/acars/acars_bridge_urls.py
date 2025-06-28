"""
ACARS Bridge Plugin URL Configuration
Dedicated API for Topsky ACARS Bridge plugin
URL Structure: /api/acars-login/
"""

from django.urls import path
from .views import acars_bridge_login

app_name = 'acars_bridge'

urlpatterns = [
    # ACARS Bridge login endpoint
    path('acars-login/', acars_bridge_login, name='acars_login'),
] 