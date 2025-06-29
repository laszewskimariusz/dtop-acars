from rest_framework import serializers
from django.contrib.auth.models import User
from .models import SmartcarsProfile


class APIInfoSerializer(serializers.Serializer):
    """Serializer for API info endpoint"""
    name = serializers.CharField()
    version = serializers.CharField()
    
    
class LoginSerializer(serializers.Serializer):
    """Serializer for login endpoint"""
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for SmartCARS API"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class SmartcarsProfileSerializer(serializers.ModelSerializer):
    """SmartCARS profile serializer"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = SmartcarsProfile
        fields = ['api_key', 'acars_token', 'created_at', 'last_login', 'user']
        read_only_fields = ['api_key', 'acars_token', 'created_at', 'last_login'] 