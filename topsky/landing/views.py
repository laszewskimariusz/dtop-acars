from django.shortcuts import render
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    try:
        logger.info("Attempting to render landing page")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"User authenticated: {request.user.is_authenticated}")
        
        context = {
            'debug_info': {
                'path': request.path,
                'method': request.method,
                'user_authenticated': request.user.is_authenticated,
            }
        }
        
        return render(request, 'landing/landing.html', context)
    except Exception as e:
        logger.error(f"Error rendering landing page: {e}")
        logger.exception("Full traceback:")
        return HttpResponse(f"<h1>Error: {e}</h1><p>Debug mode is enabled.</p>", content_type="text/html") 