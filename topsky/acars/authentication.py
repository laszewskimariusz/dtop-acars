import base64
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import SmartcarsProfile


class SmartCARSAuthentication(BaseAuthentication):
    """
    SmartCARS authentication backend supporting:
    1. Email/Password authentication 
    2. Email/API Key authentication
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None
        
        try:
            # Parse Basic Auth header
            if not auth_header.startswith('Basic '):
                return None
                
            auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
            email, password = auth_decoded.split(':', 1)
        except (ValueError, UnicodeDecodeError):
            raise AuthenticationFailed('Invalid authentication header')
        
        # Try to authenticate user
        user = self._authenticate_user(email, password)
        if user:
            return (user, None)
        
        return None
    
    def _authenticate_user(self, email, password):
        """
        Authenticate user by email/password or email/api_key
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return None
        
        # First try regular password authentication
        if user.check_password(password):
            # Update last login for SmartCARS profile
            try:
                profile = user.smartcars_profile
                profile.update_last_login()
            except SmartcarsProfile.DoesNotExist:
                # Create profile if it doesn't exist
                SmartcarsProfile.get_or_create_for_user(user)
            return user
        
        # Then try API key authentication (for Discord/VATSIM SSO users)
        try:
            profile = user.smartcars_profile
            if profile.api_key == password:
                profile.update_last_login()
                return user
        except SmartcarsProfile.DoesNotExist:
            pass
        
        return None


def authenticate_smartcars_user(email, password):
    """
    Helper function to authenticate SmartCARS user
    Returns user object or None
    """
    auth = SmartCARSAuthentication()
    
    # Create mock request with basic auth
    class MockRequest:
        def __init__(self, email, password):
            credentials = base64.b64encode(f"{email}:{password}".encode()).decode()
            self.META = {'HTTP_AUTHORIZATION': f'Basic {credentials}'}
    
    mock_request = MockRequest(email, password)
    result = auth.authenticate(mock_request)
    
    return result[0] if result else None 