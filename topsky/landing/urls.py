from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello_world, name='landing-home'),
    path('home/', views.home, name='landing-home-full'),
] 