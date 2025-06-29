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
    2. Username/Password authentication
    3. Email/API Key authentication
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
            identifier, password = auth_decoded.split(':', 1)
        except (ValueError, UnicodeDecodeError):
            raise AuthenticationFailed('Invalid authentication header')
        
        # Try to authenticate user
        user = self._authenticate_user(identifier, password)
        if user:
            return (user, None)
        
        return None
    
    def _authenticate_user(self, identifier, password):
        """
        Authenticate user by email/password, username/password, or email/api_key
        """
        # Try email first
        try:
            user = User.objects.get(email=identifier)
            if self._check_user_credentials(user, password):
                return user
        except User.DoesNotExist:
            pass
        
        # Try username
        try:
            user = User.objects.get(username=identifier)
            if self._check_user_credentials(user, password):
                return user
        except User.DoesNotExist:
            pass
        
        return None
    
    def _check_user_credentials(self, user, password):
        """
        Check if password or API key is valid for user
        """
        # First try regular password authentication
        if user.check_password(password):
            # Update last login for SmartCARS profile
            try:
                profile = user.smartcars_profile
                profile.update_last_login()
            except SmartcarsProfile.DoesNotExist:
                # Create profile if it doesn't exist
                SmartcarsProfile.get_or_create_for_user(user)
            return True
        
        # Then try API key authentication (for Discord/VATSIM SSO users)
        try:
            profile = user.smartcars_profile
            if profile.api_key == password:
                profile.update_last_login()
                return True
        except SmartcarsProfile.DoesNotExist:
            pass
        
        return False


def authenticate_smartcars_user(identifier, password):
    """
    Helper function to authenticate SmartCARS user
    Accepts email or username as identifier
    Returns user object or None
    """
    auth = SmartCARSAuthentication()
    
    # Create mock request with basic auth
    class MockRequest:
        def __init__(self, identifier, password):
            credentials = base64.b64encode(f"{identifier}:{password}".encode()).decode()
            self.META = {'HTTP_AUTHORIZATION': f'Basic {credentials}'}
    
    mock_request = MockRequest(identifier, password)
    result = auth.authenticate(mock_request)
    
    return result[0] if result else None 