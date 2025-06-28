from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from .models import ACARSMessage
from .serializers import ACARSMessageSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

# Create your views here.

def acars_dashboard(request):
    """Renderuje stronę z interfejsem ACARS"""
    return render(request, 'acars/dashboard.html')

@csrf_exempt  
@require_http_methods(["GET"])
def smartcars_handler(request):
    """
    Główny endpoint smartCARS API - pokazuje informacje o handlerze
    Kompatybilny z oczekiwaniami smartCARS 3 od TFDi Design
    """
    return JsonResponse({
        "apiVersion": "1.0.0",
        "handler": {
            "name": "Django ACARS Handler",
            "version": "1.0.0", 
            "author": "Topsky Virtual Airlines",
            "website": "https://dtopsky.topsky.app"
        },
        "status": "success",
        "response": "smartCARS API Handler is active and ready",
        "data": {
            "platform": "Django",
            "phpvms_version": "7.0.0", # Symulacja phpVMS 7 dla kompatybilności
            "features": ["ACARS", "Position Reporting", "Flight Tracking", "Authentication"],
            "endpoints": {
                "login": "/acars/api/login",
                "user": "/acars/api/user", 
                "schedules": "/acars/api/schedules",
                "aircraft": "/acars/api/aircraft",
                "airports": "/acars/api/airports",
                "webhook": "/acars/webhook"
            }
        }
    })

@csrf_exempt
@require_http_methods(["POST", "GET"])
def smartcars_webhook(request):
    """
    Endpoint dedykowany dla Smartcars - bez uwierzytelniania
    Accepts POST requests from Smartcars ACARS system
    """
    if request.method == "GET":
        # smartCARS 3 expects specific API format  
        return JsonResponse({
            "apiVersion": "1.0.0",
            "handler": {
                "name": "Django ACARS Handler",
                "version": "1.0.0",
                "author": "Django ACARS System", 
                "website": "https://dtopsky.topsky.app"
            },
            "status": "success",
            "response": "Handler is active and ready",
            "data": {
                "platform": "Django",
                "features": ["ACARS", "Position Reporting", "Flight Tracking"]
            }
        })
    
    try:
        # Parse JSON data from Smartcars
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Fallback for form data
            data = dict(request.POST.items())
        
        # Create default user for Smartcars messages if not exists
        smartcars_user, created = User.objects.get_or_create(
            username='smartcars_system',
            defaults={
                'email': 'smartcars@system.local',
                'first_name': 'Smartcars',
                'last_name': 'System'
            }
        )
        
        # Create ACARS message
        acars_message = ACARSMessage.objects.create(
            user=smartcars_user,
            aircraft_id=data.get('aircraft_id', 'UNKNOWN'),
            flight_number=data.get('flight_number', ''),
            route=data.get('route', ''),
            direction='IN',  # Incoming from Smartcars
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            altitude=data.get('altitude'),
            speed=data.get('speed'),
            heading=data.get('heading'),
            fuel_on_board=data.get('fuel_on_board'),
            pax_count=data.get('pax_count'),
            payload=data  # Store all raw data
        )
        
        # smartCARS 3 compatible response format
        return JsonResponse({
            "apiVersion": "1.0.0",
            "status": "success", 
            "response": "Message received successfully",
            "data": {
                "id": acars_message.id,
                "timestamp": acars_message.timestamp.isoformat()
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            "apiVersion": "1.0.0",
            "status": "error",
            "response": "Invalid JSON data"
        }, status=400)
    except Exception as e:
        return JsonResponse({
            "apiVersion": "1.0.0", 
            "status": "error",
            "response": str(e)
        }, status=500)

class ACARSMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ACARSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only messages for the authenticated user
        return ACARSMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@csrf_exempt
@require_http_methods(["POST"])
def smartcars_auth_login(request):
    """
    SmartCARS authentication endpoint - kompatybilny z phpVMS
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = dict(request.POST.items())
        
        # SmartCARS może wysyłać jako 'email' lub 'username'
        username = data.get('username') or data.get('email') or data.get('pilot_id')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                "status": "error",
                "message": "Username and password required"
            }, status=400)
        
        # Authenticate user
        user = authenticate(username=username, password=password)
        if not user:
            # Try email authentication
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user and user.is_active:
            # Create or get token
            token, created = Token.objects.get_or_create(user=user)
            
            # phpVMS compatible response format
            return JsonResponse({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "id": user.id,
                    "pilot_id": user.id,
                    "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                    "email": user.email,
                    "country": "PL",  # Default country
                    "timezone": "Europe/Warsaw",  # Default timezone
                    "curr_airport_id": "EPWA",  # Default current airport
                    "home_airport_id": "EPWA",  # Default home airport
                    "flights": 0,  # Default flight count
                    "flight_time": 0,  # Default flight time
                    "transfer_time": 0,  # Default transfer time
                    "rank_id": 1,  # Default rank
                    "api_key": token.key,  # API token
                    "created_at": user.date_joined.isoformat(),
                    "updated_at": user.date_joined.isoformat()
                }
            })
        else:
            return JsonResponse({
                "status": "error", 
                "message": "Invalid login credentials"
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Authentication error: {str(e)}"
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def smartcars_user_info(request):
    """
    SmartCARS user info endpoint - kompatybilny z phpVMS
    """
    # Get token from Authorization header or api_key parameter
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    api_key = request.GET.get('api_key', '')
    
    token_key = ''
    if auth_header.startswith('Bearer '):
        token_key = auth_header.replace('Bearer ', '')
    elif api_key:
        token_key = api_key
    else:
        return JsonResponse({
            "status": "error",
            "message": "Authorization header or api_key parameter required"
        }, status=401)
    
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        # phpVMS compatible response format
        return JsonResponse({
            "status": "success",
            "data": {
                "id": user.id,
                "pilot_id": user.id,
                "name": f"{user.first_name} {user.last_name}".strip() or user.username,
                "email": user.email,
                "country": "PL",  # Default country
                "timezone": "Europe/Warsaw",  # Default timezone
                "curr_airport_id": "EPWA",  # Default current airport
                "home_airport_id": "EPWA",  # Default home airport
                "flights": 0,  # Default flight count
                "flight_time": 0,  # Default flight time
                "transfer_time": 0,  # Default transfer time
                "rank_id": 1,  # Default rank
                "state": 1,  # Active state
                "is_active": user.is_active,
                "created_at": user.date_joined.isoformat(),
                "updated_at": user.date_joined.isoformat()
            }
        })
    except Token.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Invalid API key"
        }, status=401)

@csrf_exempt
@require_http_methods(["GET"])
def smartcars_basic_data(request):
    """
    SmartCARS basic data endpoint - airports, aircraft, etc.
    Kompatybilny z phpVMS - obsługuje autoryzację przez api_key
    """
    # Get token from Authorization header or api_key parameter
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    api_key = request.GET.get('api_key', '')
    
    token_key = ''
    if auth_header.startswith('Bearer '):
        token_key = auth_header.replace('Bearer ', '')
    elif api_key:
        token_key = api_key
    else:
        return JsonResponse({
            "status": "error",
            "message": "Authorization required - provide api_key parameter or Authorization header"
        }, status=401)
    
    # Verify token
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
    except Token.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Invalid API key"
        }, status=401)
    
    # Basic mock data for smartCARS to function
    return JsonResponse({
        "status": "success",
        "data": {
            "airports": [
                {
                    "id": 1,
                    "icao": "EPWA",
                    "iata": "WAW", 
                    "name": "Warsaw Chopin Airport",
                    "city": "Warsaw",
                    "country": "Poland",
                    "latitude": 52.1657,
                    "longitude": 20.9671,
                    "elevation": 374,
                    "timezone": "Europe/Warsaw",
                    "fuel_100ll_cost": 0,
                    "fuel_jeta_cost": 0,
                    "ground_handling_cost": 50
                },
                {
                    "id": 2,
                    "icao": "EPKK",
                    "iata": "KRK",
                    "name": "Krakow Airport", 
                    "city": "Krakow",
                    "country": "Poland",
                    "latitude": 50.0777,
                    "longitude": 19.7848,
                    "elevation": 794,
                    "timezone": "Europe/Warsaw",
                    "fuel_100ll_cost": 0,
                    "fuel_jeta_cost": 0,
                    "ground_handling_cost": 50
                }
            ],
            "aircraft": [
                {
                    "id": 1,
                    "registration": "SP-LWA",
                    "name": "Boeing 737-800",
                    "icao": "B738",
                    "active": 1,
                    "fuel_type": 1,
                    "max_weight": 79000,
                    "empty_weight": 41145,
                    "max_fuel": 26020,
                    "cruise_altitude": 37000,
                    "cruise_speed": 453
                },
                {
                    "id": 2, 
                    "registration": "SP-LWB",
                    "name": "Boeing 737-MAX 8",
                    "icao": "B38M",
                    "active": 1,
                    "fuel_type": 1,
                    "max_weight": 82190,
                    "empty_weight": 45070,
                    "max_fuel": 25816,
                    "cruise_altitude": 41000,
                    "cruise_speed": 453
                }
            ],
            "airlines": [
                {
                    "id": 1,
                    "icao": "LOT",
                    "iata": "LO", 
                    "name": "LOT Polish Airlines",
                    "active": 1,
                    "country": "Poland"
                }
            ]
        }
    })

@csrf_exempt
@require_http_methods(["GET"])
def smartcars_schedules(request):
    """
    SmartCARS schedules endpoint - flight schedules
    Kompatybilny z phpVMS - obsługuje autoryzację przez api_key
    """
    # Get token from Authorization header or api_key parameter
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    api_key = request.GET.get('api_key', '')
    
    token_key = ''
    if auth_header.startswith('Bearer '):
        token_key = auth_header.replace('Bearer ', '')
    elif api_key:
        token_key = api_key
    else:
        return JsonResponse({
            "status": "error",
            "message": "Authorization required - provide api_key parameter or Authorization header"
        }, status=401)
    
    # Verify token
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
    except Token.DoesNotExist:
        return JsonResponse({
            "status": "error",
            "message": "Invalid API key"
        }, status=401)
    
    # Mock flight schedules data for smartCARS
    return JsonResponse({
        "status": "success",
        "data": [
            {
                "id": 1,
                "code": "LO123",
                "flight_number": "123", 
                "airline_id": 1,
                "aircraft_id": 1,
                "dpt_airport_id": "EPWA",
                "arr_airport_id": "EPKK", 
                "dpt_time": "08:00",
                "arr_time": "09:30",
                "flight_time": 90,  # w minutach
                "distance": 252,    # w milach morskich
                "route": "EPWA DCT EPKK",
                "notes": "Regular scheduled service",
                "active": 1,
                "days": "1234567"  # wszystkie dni tygodnia
            },
            {
                "id": 2,
                "code": "LO456",
                "flight_number": "456",
                "airline_id": 1,
                "aircraft_id": 1,
                "dpt_airport_id": "EPKK",
                "arr_airport_id": "EPWA",
                "dpt_time": "10:00", 
                "arr_time": "11:30",
                "flight_time": 90,
                "distance": 252,
                "route": "EPKK DCT EPWA",
                "notes": "Return service",
                "active": 1,
                "days": "1234567"
            }
        ]
    })
