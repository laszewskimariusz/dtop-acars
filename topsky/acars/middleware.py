"""
Middleware for smartCARS API
"""

from django.http import HttpResponsePermanentRedirect
from django.conf import settings


class SmartCARSHTTPSMiddleware:
    """
    Middleware to force HTTPS for smartCARS API endpoints
    Prevents 301 redirects that smartCARS cannot handle
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Force HTTPS for smartCARS API endpoints
        if (request.path.startswith('/api/smartcars/') and 
            not request.is_secure() and 
            not settings.DEBUG):
            
            # Redirect HTTP to HTTPS
            https_url = f"https://{request.get_host()}{request.get_full_path()}"
            return HttpResponsePermanentRedirect(https_url)
        
        response = self.get_response(request)
        return response


class SmartCARSCORSMiddleware:
    """
    Add CORS headers for smartCARS API
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers for smartCARS API endpoints
        if request.path.startswith('/api/smartcars/'):
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, HEAD, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response['Access-Control-Max-Age'] = '86400'
        
        return response 