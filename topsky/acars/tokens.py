"""
Custom JWT Token Classes for SmartCARS compatibility
"""

from rest_framework_simplejwt.tokens import RefreshToken


class SmartCARSAccessToken(RefreshToken.access_token_class):
    """
    Custom JWT Access Token with SmartCARS compatibility
    Includes 'sub' claim in the token payload from the start
    """
    
    @classmethod
    def for_user(cls, user):
        """
        Create token with 'sub' claim included from the beginning
        """
        token = super().for_user(user)
        token['sub'] = user.id  # SmartCARS pilot ID claim
        return token


class SmartCARSRefreshToken(RefreshToken):
    """
    Custom JWT Refresh Token that uses SmartCARSAccessToken
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