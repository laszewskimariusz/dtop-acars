from django.shortcuts import render
from django.http import HttpResponse
import logging

logger = logging.getLogger(__name__)

def hello_world(request):
    """Simple Hello World page for testing"""
    return HttpResponse("Hello World! Railway is working!", content_type="text/plain")

def home(request):
    try:
        logger.info("Attempting to render landing page")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"User authenticated: {request.user.is_authenticated}")
        
        # Simple test response without templates
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Topsky Airlines - Test</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-slate-900 text-white p-8">
            <h1 class="text-4xl font-bold mb-4">Topsky Airlines</h1>
            <p class="text-xl">Test page - working!</p>
            <p class="mt-4">Request path: """ + request.path + """</p>
            <p>User authenticated: """ + str(request.user.is_authenticated) + """</p>
        </body>
        </html>
        """, content_type="text/html")
        
    except Exception as e:
        logger.error(f"Error rendering landing page: {e}")
        logger.exception("Full traceback:")
        return HttpResponse(f"<h1>Error: {e}</h1><p>Debug mode is enabled.</p>", content_type="text/html") 