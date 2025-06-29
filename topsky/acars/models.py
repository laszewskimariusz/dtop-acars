import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class SmartcarsProfile(models.Model):
    """
    SmartCARS profile for user authentication and ACARS integration
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='smartcars_profile')
    api_key = models.CharField(max_length=64, unique=True, blank=True)
    acars_token = models.CharField(max_length=64, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'acars_smartcars_profile'
        verbose_name = 'SmartCARS Profile'
        verbose_name_plural = 'SmartCARS Profiles'
    
    def __str__(self):
        return f"SmartCARS Profile for {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.api_key:
            self.api_key = self.generate_api_key()
        if not self.acars_token:
            self.acars_token = self.generate_acars_token()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_api_key():
        """Generate a secure API key"""
        return secrets.token_hex(32)
    
    @staticmethod
    def generate_acars_token():
        """Generate a secure ACARS token"""
        return secrets.token_hex(32)
    
    @classmethod
    def get_or_create_for_user(cls, user):
        """Get or create SmartCARS profile for user"""
        profile, created = cls.objects.get_or_create(user=user)
        return profile
    
    def update_last_login(self):
        """Update last login timestamp"""
        self.last_login = timezone.now()
        self.save(update_fields=['last_login']) 