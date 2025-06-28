"""
Custom JWT Token Classes for SmartCARS compatibility
"""

from rest_framework_simplejwt.tokens import RefreshToken


class SmartCARSAccessToken(RefreshToken.access_token_class):
    """
    Custom JWT Access Token with SmartCARS compatibility
    Adds 'sub' claim that SmartCARS expects
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    @classmethod
    def for_user(cls, user):
        """
        Create token with both 'sub' and 'user_id' claims
        """
        token = cls()
        token[cls.token_type] = cls.token_type
        token['user_id'] = user.id  # Django compatibility
        token['sub'] = user.id      # SmartCARS compatibility - pilot ID
        
        return token


class SmartCARSRefreshToken(RefreshToken):
    """
    Custom JWT Refresh Token with SmartCARS compatibility
    Uses SmartCARSAccessToken for access tokens
    """
    
    access_token_class = SmartCARSAccessToken
    
    @classmethod
    def for_user(cls, user):
        """
        Create refresh token with SmartCARS-compatible access token
        """
        token = cls()
        token['user_id'] = user.id  # Django compatibility
        token['sub'] = user.id      # SmartCARS compatibility
        
        return token 