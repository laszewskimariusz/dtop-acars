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
    SmartCARS authentication endpoint
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = dict(request.POST.items())
        
        username = data.get('username') or data.get('email')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                "success": False,
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
            
            return JsonResponse({
                "success": True,
                "message": "Login successful",
                "data": {
                    "token": token.key,
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    }
                }
            })
        else:
            return JsonResponse({
                "success": False, 
                "message": "Invalid credentials"
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            "success": False,
            "message": f"Authentication error: {str(e)}"
        }, status=500)

@csrf_exempt 
@require_http_methods(["GET"])
def smartcars_user_info(request):
    """
    SmartCARS user info endpoint
    """
    # Get token from Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return JsonResponse({
            "success": False,
            "message": "Authorization header required"
        }, status=401)
    
    token_key = auth_header.replace('Bearer ', '')
    
    try:
        token = Token.objects.get(key=token_key)
        user = token.user
        
        return JsonResponse({
            "success": True,
            "data": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "is_active": user.is_active
            }
        })
    except Token.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "Invalid token"
        }, status=401)

@csrf_exempt
@require_http_methods(["GET"])
def smartcars_basic_data(request):
    """
    SmartCARS basic data endpoint - airports, aircraft, etc.
    """
    # Basic mock data for smartCARS to function
    return JsonResponse({
        "success": True,
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
                    "longitude": 20.9671
                },
                {
                    "id": 2,
                    "icao": "EPKK",
                    "iata": "KRK",
                    "name": "Krakow Airport", 
                    "city": "Krakow",
                    "country": "Poland",
                    "latitude": 50.0777,
                    "longitude": 19.7848
                }
            ],
            "aircraft": [
                {
                    "id": 1,
                    "registration": "SP-LWA",
                    "type": "Boeing 737-800",
                    "icao": "B738",
                    "active": True
                },
                {
                    "id": 2, 
                    "registration": "SP-LWB",
                    "type": "Boeing 737-MAX 8",
                    "icao": "B38M",
                    "active": True
                }
            ],
            "airlines": [
                {
                    "id": 1,
                    "icao": "LOT",
                    "iata": "LO", 
                    "name": "LOT Polish Airlines",
                    "active": True
                }
            ]
        }
    })
