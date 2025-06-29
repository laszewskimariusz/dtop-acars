from django.shortcuts import render
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def home(request):
    try:
        logger.info("Attempting to render landing page")
        return render(request, 'landing/landing.html')
    except Exception as e:
        logger.error(f"Error rendering landing page: {e}")
        return HttpResponse(f"<h1>Error: {e}</h1><p>Debug mode is enabled.</p>".encode('utf-8'), content_type="text/html") 