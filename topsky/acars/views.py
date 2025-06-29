import json
import logging
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .authentication import SmartCARSAuthentication, authenticate_smartcars_user
from .models import SmartcarsProfile
from .serializers import APIInfoSerializer, LoginSerializer, SmartcarsProfileSerializer

# Set up logging
logger = logging.getLogger(__name__)

def log_request_details(request, endpoint_name):
    """Log detailed request information"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"\n[{timestamp}] 🔍 SmartCARS Request to {endpoint_name}")
    print(f"[{timestamp}] =======================================")
    print(f"[{timestamp}] 📤 Method: {request.method}")
    print(f"[{timestamp}] 📤 Path: {request.path}")
    print(f"[{timestamp}] 📤 Content-Type: {request.content_type}")
    print(f"[{timestamp}] 📤 User-Agent: {request.META.get('HTTP_USER_AGENT', 'N/A')}")
    
    # Log all headers
    print(f"[{timestamp}] 📤 Headers:")
    for key, value in request.META.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].replace('_', '-').title()
            print(f"[{timestamp}]    {header_name}: {value}")
    
    # Log body content
    if request.body:
        try:
            if request.content_type == 'application/json':
                body_data = json.loads(request.body)
                print(f"[{timestamp}] 📤 JSON Body: {json.dumps(body_data, indent=2)}")
            else:
                print(f"[{timestamp}] 📤 Raw Body: {request.body.decode('utf-8', errors='ignore')}")
        except:
            print(f"[{timestamp}] 📤 Body (bytes): {request.body}")
    
    # Log POST data
    if request.POST:
        print(f"[{timestamp}] 📤 POST Data: {dict(request.POST.items())}")
    
    # Log GET parameters
    if request.GET:
        print(f"[{timestamp}] 📤 GET Params: {dict(request.GET.items())}")
    
    print(f"[{timestamp}] =======================================")

def log_response_details(response_data, status_code, endpoint_name):
    """Log response details"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    print(f"[{timestamp}] 📥 Response from {endpoint_name}")
    print(f"[{timestamp}] 📥 Status: {status_code}")
    print(f"[{timestamp}] 📥 Data: {json.dumps(response_data, indent=2)}")
    print(f"[{timestamp}] =======================================\n")


# SmartCARS API Info endpoint - required by SmartCARS
@csrf_exempt
@require_http_methods(["GET"])
def api_info(request):
    """
    SmartCARS API info endpoint
    This endpoint is called by SmartCARS to verify the API is working
    """
    log_request_details(request, "API_INFO")
    
    data = {
        "name": "Topsky Virtual Airlines SmartCARS API",
        "version": "1.0.0",
        "apiVersion": "1.0.0",
        "handler": "django", 
        "description": "SmartCARS 3 API for Topsky Virtual Airlines",
        "endpoints": {
            "login": "/api/smartcars/login",
            "pilot": "/api/smartcars/pilot",
            "data": "/api/smartcars/data"
        }
    }
    
    log_response_details(data, 200, "API_INFO")
    return JsonResponse(data)


# Login endpoint for SmartCARS
@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    SmartCARS login endpoint
    Accepts email/password, username/password, or email/api_key authentication
    Supports JSON body, form data, and Basic Auth
    """
    log_request_details(request, "LOGIN")
    
    try:
        identifier = None  # Can be email or username
        password = None
        
        # Check for Basic Auth header first (SmartCARS may use this)
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if auth_header and auth_header.startswith('Basic '):
            try:
                import base64
                auth_decoded = base64.b64decode(auth_header[6:]).decode('utf-8')
                identifier, password = auth_decoded.split(':', 1)
                print(f"🔐 Using Basic Auth - Identifier: {identifier}")
            except (ValueError, UnicodeDecodeError):
                error_data = {'error': 'Invalid authentication header'}
                log_response_details(error_data, 400, "LOGIN")
                return JsonResponse(error_data, status=400)
        
        # If no Basic Auth, try JSON body
        elif request.content_type == 'application/json' and request.body:
            data = json.loads(request.body)
            # Try email first, then username
            identifier = data.get('email') or data.get('username')
            password = data.get('password')
            print(f"🔐 Using JSON Auth - Identifier: {identifier}")
        
        # If no JSON, try form data
        elif request.POST:
            # Try email first, then username
            identifier = request.POST.get('email') or request.POST.get('username')
            password = request.POST.get('password')
            print(f"🔐 Using Form Auth - Identifier: {identifier}")
        
        if not identifier or not password:
            error_data = {'error': 'Email/username and password are required'}
            log_response_details(error_data, 400, "LOGIN")
            return JsonResponse(error_data, status=400)
        
        print(f"🔐 Attempting authentication for: {identifier}")
        
        # Authenticate user (now supports both email and username)
        user = authenticate_smartcars_user(identifier, password)
        
        if user:
            print(f"✅ Authentication successful for: {identifier}")
            
            # Get or create SmartCARS profile
            profile = SmartcarsProfile.get_or_create_for_user(user)
            profile.update_last_login()
            
            # Return success response with user data
            response_data = {
                'status': 'success',
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'pilotID': f"TSK{user.id:04d}",  # Generate pilot ID
                    'username': user.username,
                    'email': user.email,
                    'firstName': user.first_name,
                    'lastName': user.last_name,
                    'session': profile.acars_token,
                    'rank': 'Pilot',
                    'rankLevel': 1,
                    'avatar': None
                },
                'session': profile.acars_token
            }
            
            log_response_details(response_data, 200, "LOGIN")
            return JsonResponse(response_data)
        else:
            print(f"❌ Authentication failed for: {identifier}")
            error_data = {'error': 'Invalid credentials'}
            log_response_details(error_data, 401, "LOGIN")
            return JsonResponse(error_data, status=401)
            
    except json.JSONDecodeError:
        print(f"❌ JSON decode error")
        error_data = {'error': 'Invalid JSON data'}
        log_response_details(error_data, 400, "LOGIN")
        return JsonResponse(error_data, status=400)
    except Exception as e:
        print(f"❌ Exception during login: {e}")
        error_data = {'error': 'Internal server error'}
        log_response_details(error_data, 500, "LOGIN")
        return JsonResponse(error_data, status=500)


# Pilot info endpoint (requires authentication)
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def pilot_info(request):
    """
    Get pilot information - requires authentication
    """
    log_request_details(request, "PILOT_INFO")
    
    user = request.user
    profile = SmartcarsProfile.get_or_create_for_user(user)
    
    response_data = {
        'id': user.id,
        'pilotID': f"TSK{user.id:04d}",
        'username': user.username,
        'email': user.email,
        'firstName': user.first_name,
        'lastName': user.last_name,
        'rank': 'Pilot',
        'rankLevel': 1,
        'avatar': None,
        'session': profile.acars_token,
        'stats': {
            'totalFlights': 0,
            'totalHours': 0,
            'totalDistance': 0
        }
    }
    
    log_response_details(response_data, 200, "PILOT_INFO")
    return Response(response_data)


# Basic data endpoint
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def data_info(request):
    """
    Basic data endpoint for SmartCARS
    """
    log_request_details(request, "DATA_INFO")
    
    response_data = {
        'airline': {
            'name': 'Topsky Virtual Airlines',
            'icao': 'TSK',
            'iata': 'TS',
            'logo': '/static/images/logo.png'
        },
        'settings': {
            'currency': 'USD',
            'timezone': 'UTC',
            'units': 'imperial'
        }
    }
    
    log_response_details(response_data, 200, "DATA_INFO")
    return Response(response_data)


# Test endpoint to verify authentication
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """
    Test endpoint to verify authentication is working
    """
    log_request_details(request, "TEST_AUTH")
    
    response_data = {
        'status': 'authenticated',
        'user': request.user.username,
        'email': request.user.email
    }
    
    log_response_details(response_data, 200, "TEST_AUTH")
    return Response(response_data) 