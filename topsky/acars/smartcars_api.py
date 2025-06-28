"""
Official smartCARS 3 API Implementation for Django
Based on invernyx/smartcars-3-phpvms7-api official module
Compatible with TFDi Design smartCARS 3 application
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import get_object_or_404
from .models import ACARSMessage
from .serializers import ACARSMessageSerializer
import datetime
from django.utils import timezone
from datetime import timedelta
import logging


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([JSONParser, FormParser])
def debug_login(request):
    """
    Debug endpoint do testowania co SmartCARS wysyła
    """
    # Zaloguj na konsoli Django, co przyszło
    print(">> DEBUG_LOGIN request.content_type:", request.content_type)
    print(">> DEBUG_LOGIN request.data:", request.data)
    print(">> DEBUG_LOGIN request.GET:", request.GET)
    print(">> DEBUG_LOGIN request.POST:", request.POST)
    print(">> DEBUG_LOGIN request.body:", request.body)

    # Wyciągnij pola
    username = request.data.get('username') or request.data.get('email')
    password = request.data.get('password') or request.data.get('api_key')
    print(">> DEBUG_LOGIN username:", username, "password:", password)

    # Na potrzeby testu zwróć "success" zawsze
    now = timezone.now()
    return Response({
        "pilotID":   "LO9999",
        "session":   "TESTTOKEN123",
        "expiry":    int((now + timedelta(hours=1)).timestamp()),
        "firstName": "Test",
        "lastName":  "User",
        "email":     username or "test@example.com"
    })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def acars_login(request):
    """
    Standard PHPvMS5 compatible ACARS Login Endpoint
    Expected at: /api/acars-login/
    
    SmartCARS sends:
    - Content-Type: application/x-www-form-urlencoded
    - Fields: username (email), password (Django password)
    
    Returns API key as session token for ACARS communication
    """
    logger = logging.getLogger(__name__)
    User = get_user_model()
    
    # Handle GET requests (ACARS may send GET first to check endpoint)
    if request.method == 'GET':
        return Response({
            "apiVersion": "1.0.2",
            "handler": {
                "name": "smartCARS 3 Pilot Login",
                "version": "1.0.2",
                "author": "Topsky Virtual Airlines",
                "web": "https://dtopsky.topsky.app"
            },
            "phpvms": {
                "version": "7.0.0",
                "type": "Django Port"
            },
            "auth": True,
            "message": "Login endpoint ready. Send POST with username and password.",
            "methods": ["POST"],
            "fields": ["username", "password"]
        }, status=status.HTTP_200_OK)
    
    # Debug logging for POST requests
    print(">> ACARS_LOGIN request.content_type:", request.content_type)
    print(">> ACARS_LOGIN request.data:", request.data)
    
    # Extract credentials - various field names for compatibility
    username = (request.data.get('username') or 
               request.data.get('email') or 
               request.data.get('user_id'))
    
    password = (request.data.get('password') or 
               request.data.get('user_password'))
    
    if not username or not password:
        return Response({
            "message": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Authenticate user with Django password
    user = None
    try:
        # Method 1: Try email lookup + Django password check
        try:
            user = User.objects.get(email__iexact=username, is_active=True)
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None
            
        # Method 2: Try username lookup + Django password check  
        if not user:
            try:
                user = User.objects.get(username__iexact=username, is_active=True)
                if not user.check_password(password):
                    user = None
            except User.DoesNotExist:
                user = None
        
        # Method 3: Try Django authenticate as fallback
        if not user:
            user = authenticate(username=username, password=password)
            
    except Exception as e:
        logger.error(f"ACARS login error: {e}")
        user = None
    
    if not user or not user.is_active:
        return Response({
            "message": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    try:
        # Get or create SmartCARS profile for the user
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.get_or_create_for_user(user)
        
        # Update last used timestamp
        profile.last_used = timezone.now()
        profile.save(update_fields=['last_used'])
        
        # Calculate expiry (7 days from now - SmartCARS 3 standard)
        expiry_time = timezone.now() + timedelta(days=7)
        expiry_timestamp = int(expiry_time.timestamp())
        
        # Generate pilot ID in SmartCARS format
        pilot_id = f"LO{user.id:04d}"
        
        # Standard PHPvMS5/SmartCARS compatible response format
        # Return SmartCARS API key as session token (not JWT)
        return Response({
            "pilotID": pilot_id,
            "session": profile.api_key,  # SmartCARS API key as session token
            "expiry": expiry_timestamp,
            "firstName": user.first_name or user.username.split('@')[0],
            "lastName": user.last_name or "",
            "email": user.email
        })
        
    except Exception as e:
        logger.error(f"ACARS token generation error: {e}")
        return Response({
            "message": "Authentication failed"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def handler(request):
    """
    Official smartCARS 3 API Handler - Main Entry Point
    Compatible with TFDi Design smartCARS 3 application
    Format based on official phpVMS 7 module: github.com/invernyx/smartcars-3-phpvms7-api
    """
    return Response({
        "apiVersion": "1.0.2",
        "handler": {
            "name": "smartCARS 3 Django Handler",
            "version": "1.0.2",
            "author": "Topsky Virtual Airlines",
            "web": "https://dtopsky.topsky.app"
        },
        "phpvms": {
            "version": "7.0.0",
            "type": "Django Port"
        },
        "auth": True,
        "time": datetime.datetime.now().isoformat() + "Z"
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def user(request):
    """
    Official smartCARS 3 User Info Endpoint
    Returns user information for authenticated session
    Supports both JWT tokens and SmartCARS API keys
    """
    User = get_user_model()
    user = None
    
    # Extract session token from Authorization header or session parameter
    session_token = request.GET.get('session')
    
    # Method 1: Try SmartCARS API key authentication
    if session_token:
        try:
            from .models import SmartcarsProfile
            profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
            user = profile.user
        except SmartcarsProfile.DoesNotExist:
            pass
    
    # Method 2: Try JWT authentication if no API key found
    if not user:
        if session_token and not request.META.get('HTTP_AUTHORIZATION'):
            request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
        
        jwt_auth = JWTAuthentication()
        try:
            user_auth = jwt_auth.authenticate(request)
            if user_auth:
                user, token = user_auth
        except Exception:
            pass
    
    if user and user.is_active:
        return Response({
            "pilot_id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "country": "PL",
            "timezone": "Europe/Warsaw",
            "opt_in": True,
            "status": 1,
            "total_flights": ACARSMessage.objects.filter(user=user).count(),
            "total_hours": 0,  # Can be calculated from flight data
            "curr_airport_id": "EPWA"  # Default current airport
        })
    else:
        return Response({
            "message": "Authentication required"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def schedules(request):
    """
    Official smartCARS 3 Schedules Endpoint
    Returns available flight schedules for the virtual airline
    """
    # Authenticate user
    session_token = request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        # Sample schedule data - can be extended with real database
        schedules = [
            {
                "id": 1,
                "airline_id": 1,
                "flight_number": "TS001",
                "route_code": "EPWA-EGLL",
                "dpt_airport_id": "EPWA",
                "arr_airport_id": "EGLL",
                "aircraft_id": 1,
                "distance": 1200,
                "flight_time": 120,
                "route": "EPWA DCT EGLL",
                "notes": "Regular passenger service",
                "active": True
            },
            {
                "id": 2,
                "airline_id": 1,
                "flight_number": "TS002",
                "route_code": "EGLL-EPWA",
                "dpt_airport_id": "EGLL",
                "arr_airport_id": "EPWA",
                "aircraft_id": 2,
                "distance": 1200,
                "flight_time": 120,
                "route": "EGLL DCT EPWA",
                "notes": "Return passenger service",
                "active": True
            }
        ]
        
        return Response(schedules)
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def aircraft(request):
    """
    Official smartCARS 3 Aircraft Endpoint
    Returns available aircraft for the virtual airline
    """
    # Authenticate user
    session_token = request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        # Sample aircraft data - can be extended with real database
        aircraft = [
            {
                "id": 1,
                "icao": "B738",
                "iata": "738",
                "name": "Boeing 737-800",
                "registration": "SP-TSA",
                "hex_code": "48421F",
                "active": True,
                "subfleet_id": 1
            },
            {
                "id": 2,
                "icao": "A320",
                "iata": "320",
                "name": "Airbus A320-200",
                "registration": "SP-TSB",
                "hex_code": "48422F",
                "active": True,
                "subfleet_id": 2
            }
        ]
        
        return Response(aircraft)
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def airports(request):
    """
    Official smartCARS 3 Airports Endpoint
    Returns available airports for the virtual airline
    """
    # Authenticate user
    session_token = request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        # Sample airport data - can be extended with real database
        airports = [
            {
                "id": "EPWA",
                "icao": "EPWA",
                "iata": "WAW",
                "name": "Warsaw Chopin Airport",
                "location": "Warsaw, Poland",
                "country": "PL",
                "lat": 52.1656900,
                "lng": 20.9670900,
                "hub": True
            },
            {
                "id": "EGLL",
                "icao": "EGLL",
                "iata": "LHR",
                "name": "London Heathrow Airport",
                "location": "London, United Kingdom",
                "country": "GB",
                "lat": 51.4700200,
                "lng": -0.4542600,
                "hub": False
            },
            {
                "id": "EDDF",
                "icao": "EDDF",
                "iata": "FRA",
                "name": "Frankfurt am Main Airport",
                "location": "Frankfurt, Germany",
                "country": "DE",
                "lat": 50.0264400,
                "lng": 8.5431600,
                "hub": False
            }
        ]
        
        return Response(airports)
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def bid(request):
    """
    Official smartCARS 3 Bid Endpoint
    Allows pilots to bid on flights
    """
    # Authenticate user
    session_token = request.data.get('session') or request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        flight_id = request.data.get('flight_id')
        aircraft_id = request.data.get('aircraft_id')
        
        if not flight_id:
            return Response({
                "message": "Flight ID is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create bid record (simplified - you can extend with real database model)
        bid_data = {
            "id": f"bid_{user.id}_{flight_id}",
            "user_id": user.id,
            "flight_id": flight_id,
            "aircraft_id": aircraft_id,
            "created_at": datetime.datetime.now().isoformat() + "Z"
        }
        
        return Response({
            "bid": bid_data,
            "message": "Bid created successfully"
        })
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def position(request):
    """
    Official smartCARS 3 Position Reporting Endpoint
    Receives and stores aircraft position data during flight
    """
    # Authenticate user
    session_token = request.data.get('session') or request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        # Extract position data
        position_data = {
            'latitude': request.data.get('lat'),
            'longitude': request.data.get('lng'),
            'altitude': request.data.get('altitude'),
            'heading': request.data.get('heading'),
            'speed': request.data.get('speed'),
            'aircraft_id': request.data.get('aircraft'),
            'flight_number': request.data.get('flight_number'),
            'direction': 'OUT',  # Position report
            'payload': dict(request.data)  # Store full smartCARS data
        }
        
        # Create ACARS message with position data
        serializer = ACARSMessageSerializer(data=position_data)
        if serializer.is_valid():
            message = serializer.save(user=user)
            
            return Response({
                "message": "Position updated successfully",
                "id": message.id if message else None
            })
        else:
            return Response({
                "message": "Invalid position data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def pirep(request):
    """
    Official smartCARS 3 PIREP (Pilot Report) Endpoint
    Receives and processes completed flight reports
    """
    # Authenticate user
    session_token = request.data.get('session') or request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if not user_auth:
            return Response({
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user, token = user_auth
        
        # Extract PIREP data
        pirep_data = {
            'flight_number': request.data.get('flight_number'),
            'aircraft_id': request.data.get('aircraft'),
            'departure_airport': request.data.get('dpt_airport'),
            'arrival_airport': request.data.get('arr_airport'),
            'flight_time': request.data.get('flight_time'),
            'distance': request.data.get('distance'),
            'fuel_used': request.data.get('fuel_used'),
            'landing_rate': request.data.get('landing_rate'),
            'direction': 'IN',  # Completed flight report
            'payload': dict(request.data)  # Store full PIREP data
        }
        
        # Create ACARS message with PIREP data
        serializer = ACARSMessageSerializer(data=pirep_data)
        if serializer.is_valid():
            message = serializer.save(user=user)
            
            return Response({
                "pirep_id": message.id if message else None,
                "message": "PIREP submitted successfully",
                "status": "pending"  # Can be auto-accepted based on rules
            })
        else:
            return Response({
                "message": "Invalid PIREP data",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED) 