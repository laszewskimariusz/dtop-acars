from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ACARSMessageViewSet, acars_dashboard, smartcars_webhook

router = DefaultRouter()
router.register(r'messages', ACARSMessageViewSet, basename='acarsmessage')

urlpatterns = [
    path('', acars_dashboard, name='acars_dashboard'),
    path('webhook/', smartcars_webhook, name='smartcars_webhook'),
    path('api/', include(router.urls)),
] 