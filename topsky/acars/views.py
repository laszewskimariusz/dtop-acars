import json
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


# SmartCARS API Info endpoint - required by SmartCARS
@csrf_exempt
@require_http_methods(["GET"])
def api_info(request):
    """
    SmartCARS API info endpoint
    This endpoint is called by SmartCARS to verify the API is working
    """
    data = {
        "name": "Topsky Virtual Airlines SmartCARS API",
        "version": "1.0.0",
        "handler": "django",
        "description": "SmartCARS 3 API for Topsky Virtual Airlines",
        "endpoints": {
            "login": "/api/smartcars/login",
            "pilot": "/api/smartcars/pilot",
            "data": "/api/smartcars/data"
        }
    }
    return JsonResponse(data)


# Login endpoint for SmartCARS
@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    SmartCARS login endpoint
    Accepts email/password or email/api_key authentication
    """
    try:
        # Parse JSON body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')
        else:
            # Try form data
            email = request.POST.get('email')
            password = request.POST.get('password')
        
        if not email or not password:
            return JsonResponse({
                'error': 'Email and password are required'
            }, status=400)
        
        # Authenticate user
        user = authenticate_smartcars_user(email, password)
        
        if user:
            # Get or create SmartCARS profile
            profile = SmartcarsProfile.get_or_create_for_user(user)
            profile.update_last_login()
            
            # Return success response with user data
            return JsonResponse({
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
            })
        else:
            return JsonResponse({
                'error': 'Invalid credentials'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': 'Internal server error'
        }, status=500)


# Pilot info endpoint (requires authentication)
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def pilot_info(request):
    """
    Get pilot information - requires authentication
    """
    user = request.user
    profile = SmartcarsProfile.get_or_create_for_user(user)
    
    return Response({
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
    })


# Basic data endpoint
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def data_info(request):
    """
    Basic data endpoint for SmartCARS
    """
    return Response({
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
    })


# Test endpoint to verify authentication
@api_view(['GET'])
@authentication_classes([SmartCARSAuthentication])
@permission_classes([IsAuthenticated])
def test_auth(request):
    """
    Test endpoint to verify authentication is working
    """
    return Response({
        'status': 'authenticated',
        'user': request.user.username,
        'email': request.user.email
    }) 