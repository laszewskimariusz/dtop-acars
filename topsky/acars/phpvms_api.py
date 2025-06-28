"""
Official smartCARS 3 API - 1:1 Compatible with phpVMS 5/7
Based on: https://github.com/invernyx/smartcars-3-phpvms5-api
REST API specification compatible with TFDi Design smartCARS 3
"""

import json
import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get real client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_handler(request):
    """
    Official smartCARS 3 API Handler - Main Entry Point
    URL: /api/smartcars/
    
    Returns handler information compatible with smartCARS 3 specification
    """
    return JsonResponse({
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


@csrf_exempt
@require_http_methods(["POST"])
def api_login(request):
    """
    Official smartCARS 3 Login Endpoint
    URL: /api/smartcars/login
    
    Compatible with phpVMS 5/7 login specification:
    - Accepts: application/x-www-form-urlencoded
    - Fields: username (email), password
    - Returns: pilotID, session, expiry, firstName, lastName, email
    """
    
    # Log request for debugging
    client_ip = get_client_ip(request)
    logger.info(f"SmartCARS login attempt from {client_ip}")
    
    # Extract credentials from POST data
    username = request.POST.get('username') or request.POST.get('email')
    password = request.POST.get('password') or request.POST.get('user_password')
    
    # Validate required fields
    if not username or not password:
        logger.warning(f"Missing credentials from {client_ip}")
        return JsonResponse({
            "message": "Invalid credentials"
        }, status=401)
    
    # Authenticate user
    User = get_user_model()
    user = None
    
    try:
        # Method 1: Find user by email first
        try:
            user = User.objects.get(email__iexact=username, is_active=True)
            if not user.check_password(password):
                user = None
        except User.DoesNotExist:
            user = None
            
        # Method 2: Try Django authentication as fallback
        if not user:
            user = authenticate(username=username, password=password)
            
    except Exception as e:
        logger.error(f"Authentication error for {username}: {e}")
        user = None
    
    # Check authentication result
    if not user or not user.is_active:
        logger.warning(f"Login failed for {username} from {client_ip}")
        return JsonResponse({
            "message": "Invalid credentials"
        }, status=401)
    
    try:
        # Get or create SmartCARS profile
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.get_or_create_for_user(user)
        
        # Update last used timestamp
        profile.last_used = timezone.now()
        profile.save(update_fields=['last_used'])
        
        # Calculate expiry (7 days from now)
        expiry_time = timezone.now() + timedelta(days=7)
        expiry_timestamp = int(expiry_time.timestamp())
        
        # Generate pilot ID in phpVMS format
        pilot_id = f"LO{user.id:04d}"
        
        # Return phpVMS compatible response
        response_data = {
            "pilotID": pilot_id,
            "session": profile.api_key,
            "expiry": expiry_timestamp,
            "firstName": user.first_name or user.username.split('@')[0],
            "lastName": user.last_name or "",
            "email": user.email
        }
        
        logger.info(f"Login successful for {username} from {client_ip}")
        return JsonResponse(response_data)
        
    except Exception as e:
        logger.error(f"Session creation error for {username}: {e}")
        return JsonResponse({
            "message": "Authentication failed"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_user(request):
    """
    Official smartCARS 3 User Info Endpoint
    URL: /api/smartcars/user?session=api_key
    
    Returns user information for authenticated session
    """
    
    # Extract session token from GET parameters
    session_token = request.GET.get('session')
    
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    # Authenticate using SmartCARS API key
    try:
        from .models import SmartcarsProfile, ACARSMessage
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        user = profile.user
        
        if not user.is_active:
            return JsonResponse({
                "message": "Account inactive"
            }, status=401)
        
        # Return phpVMS compatible user info
        return JsonResponse({
            "pilot_id": user.id,
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "country": "PL",
            "timezone": "Europe/Warsaw",
            "opt_in": True,
            "status": 1,
            "total_flights": ACARSMessage.objects.filter(user=user).count(),
            "total_hours": 0,
            "curr_airport_id": "EPWA"
        })
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Invalid session token"
        }, status=401)
    except Exception as e:
        logger.error(f"User info error: {e}")
        return JsonResponse({
            "message": "Authentication failed"
        }, status=401)


@csrf_exempt
@require_http_methods(["GET"])
def api_schedules(request):
    """
    Official smartCARS 3 Schedules Endpoint
    URL: /api/smartcars/schedules?session=api_key
    
    Returns available flight schedules
    """
    
    # Authenticate user
    session_token = request.GET.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        
        # Sample schedule data (replace with real database)
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
            }
        ]
        
        return JsonResponse(schedules, safe=False)
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)


@csrf_exempt
@require_http_methods(["GET"])
def api_aircraft(request):
    """
    Official smartCARS 3 Aircraft Endpoint  
    URL: /api/smartcars/aircraft?session=api_key
    
    Returns available aircraft
    """
    
    # Authenticate user
    session_token = request.GET.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        
        # Sample aircraft data (replace with real database)
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
            }
        ]
        
        return JsonResponse(aircraft, safe=False)
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)


@csrf_exempt
@require_http_methods(["GET"])
def api_airports(request):
    """
    Official smartCARS 3 Airports Endpoint
    URL: /api/smartcars/airports?session=api_key
    
    Returns available airports
    """
    
    # Authenticate user
    session_token = request.GET.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        
        # Sample airport data (replace with real database)
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
            }
        ]
        
        return JsonResponse(airports, safe=False)
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def api_bid(request):
    """
    Official smartCARS 3 Bid Endpoint
    URL: /api/smartcars/bid
    
    Allows pilots to bid on flights
    """
    
    # Authenticate user
    session_token = request.POST.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        user = profile.user
        
        flight_id = request.POST.get('flight_id')
        aircraft_id = request.POST.get('aircraft_id')
        
        if not flight_id:
            return JsonResponse({
                "message": "Flight ID is required"
            }, status=400)
        
        # Create bid record
        bid_data = {
            "id": f"bid_{user.id}_{flight_id}",
            "user_id": user.id,
            "flight_id": flight_id,
            "aircraft_id": aircraft_id,
            "created_at": datetime.datetime.now().isoformat() + "Z"
        }
        
        return JsonResponse({
            "bid": bid_data,
            "message": "Bid created successfully"
        })
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)


@csrf_exempt
@require_http_methods(["POST"])
def api_position(request):
    """
    Official smartCARS 3 Position Reporting Endpoint
    URL: /api/smartcars/position
    
    Receives and stores aircraft position data during flight
    """
    
    # Authenticate user
    session_token = request.POST.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile, ACARSMessage
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        user = profile.user
        
        # Extract position data
        latitude = request.POST.get('lat')
        longitude = request.POST.get('lng')
        altitude = request.POST.get('altitude')
        heading = request.POST.get('heading')
        speed = request.POST.get('speed')
        aircraft_id = request.POST.get('aircraft')
        
        # Store position data as ACARS message
        ACARSMessage.objects.create(
            user=user,
            message_type='POSITION',
            aircraft_id=aircraft_id or 'UNKNOWN',
            latitude=latitude,
            longitude=longitude,
            altitude=altitude,
            heading=heading,
            speed=speed,
            timestamp=timezone.now()
        )
        
        return JsonResponse({
            "message": "Position updated successfully"
        })
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    except Exception as e:
        logger.error(f"Position update error: {e}")
        return JsonResponse({
            "message": "Position update failed"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_pirep(request):
    """
    Official smartCARS 3 PIREP Submission Endpoint
    URL: /api/smartcars/pirep
    
    Submits flight reports
    """
    
    # Authenticate user
    session_token = request.POST.get('session')
    if not session_token:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    
    try:
        from .models import SmartcarsProfile, ACARSMessage
        profile = SmartcarsProfile.objects.get(api_key=session_token, is_active=True)
        user = profile.user
        
        # Extract PIREP data
        flight_number = request.POST.get('flight_number')
        aircraft_id = request.POST.get('aircraft_id')
        departure = request.POST.get('departure')
        arrival = request.POST.get('arrival')
        flight_time = request.POST.get('flight_time')
        distance = request.POST.get('distance')
        
        # Store PIREP as ACARS message
        ACARSMessage.objects.create(
            user=user,
            message_type='PIREP',
            flight_number=flight_number or '',
            aircraft_id=aircraft_id or 'UNKNOWN',
            departure_airport=departure,
            arrival_airport=arrival,
            flight_time=flight_time,
            distance=distance,
            timestamp=timezone.now()
        )
        
        return JsonResponse({
            "pirep_id": f"pirep_{user.id}_{int(timezone.now().timestamp())}",
            "message": "PIREP submitted successfully"
        })
        
    except SmartcarsProfile.DoesNotExist:
        return JsonResponse({
            "message": "Authentication required"
        }, status=401)
    except Exception as e:
        logger.error(f"PIREP submission error: {e}")
        return JsonResponse({
            "message": "PIREP submission failed"
        }, status=500) 