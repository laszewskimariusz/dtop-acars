from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action, parser_classes
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import ACARSMessage
from .serializers import ACARSMessageSerializer, ACARSMessageReadSerializer
from django.contrib.auth import get_user_model
import datetime

# Globalna lista do przechowywania ostatnich requestów (tylko do debugowania)
RECENT_REQUESTS = []

def add_debug_request(request, response_data=None):
    """Dodaj request do listy debugowej"""
    import datetime
    
    # Bezpieczne czytanie body (unikaj RawPostDataException)
    safe_body = None
    try:
        safe_body = request.body.decode('utf-8', errors='ignore')[:500] if request.body else None
    except Exception:
        safe_body = "Unable to read body (already parsed by DRF)"
    
    debug_info = {
        'timestamp': datetime.datetime.now().isoformat(),
        'method': request.method,
        'path': request.path,
        'content_type': getattr(request, 'content_type', 'unknown'),
        'headers': dict(request.headers),
        'GET_params': dict(request.GET),
        'POST_data': dict(request.POST),
        'JSON_data': dict(request.data) if hasattr(request.data, 'items') else str(request.data),
        'body': safe_body,
        'response': response_data
    }
    
    RECENT_REQUESTS.append(debug_info)
    # Zachowaj tylko ostatnie 20 requestów
    if len(RECENT_REQUESTS) > 20:
        RECENT_REQUESTS.pop(0)

@api_view(['GET'])
@permission_classes([AllowAny])
def debug_requests(request):
    """Endpoint do przeglądania ostatnich requestów"""
    return Response({
        'recent_requests': RECENT_REQUESTS,
        'total_requests': len(RECENT_REQUESTS),
        'instructions': 'Wykonaj POST request do /acars/api/login/ żeby zobaczyć dane w tej liście'
    })

class ACARSMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet dla wiadomości ACARS
    Zapewnia pełny CRUD dla wiadomości ACARS z automatycznym przypisaniem użytkownika
    """
    serializer_class = ACARSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Zwraca tylko wiadomości należące do zalogowanego użytkownika
        """
        return ACARSMessage.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Używa różnych serializerów dla różnych akcji
        """
        if self.action in ['list', 'retrieve']:
            return ACARSMessageReadSerializer
        return ACARSMessageSerializer
    
    def perform_create(self, serializer):
        """
        Automatycznie przypisuje zalogowanego użytkownika do nowej wiadomości
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """
        Zwraca najnowszą wiadomość ACARS dla zalogowanego użytkownika
        """
        latest_message = self.get_queryset().first()
        if latest_message:
            serializer = self.get_serializer(latest_message)
            return Response(serializer.data)
        return Response({'detail': 'Brak wiadomości ACARS'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Zwraca podstawowe statystyki wiadomości ACARS dla użytkownika
        """
        queryset = self.get_queryset()
        stats = {
            'total_messages': queryset.count(),
            'incoming_messages': queryset.filter(direction='IN').count(),
            'outgoing_messages': queryset.filter(direction='OUT').count(),
            'unique_aircraft': queryset.values('aircraft_id').distinct().count(),
            'unique_flights': queryset.exclude(flight_number='').values('flight_number').distinct().count(),
        }
        return Response(stats)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ping(request):
    """
    Endpoint testowy do weryfikacji uwierzytelnienia JWT
    """
    return Response({
        'status': 'ok',
        'message': 'Uwierzytelnienie JWT działa poprawnie',
        'user': request.user.username,
        'user_id': request.user.id
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_create_messages(request):
    """
    Endpoint do masowego tworzenia wiadomości ACARS
    Przydatny gdy urządzenie ACARS wysyła wiele wiadomości jednocześnie
    """
    if not isinstance(request.data, list):
        return Response({
            'error': 'Dane muszą być listą wiadomości'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    created_messages = []
    errors = []
    
    for i, message_data in enumerate(request.data):
        serializer = ACARSMessageSerializer(data=message_data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            created_messages.append(serializer.data)
        else:
            errors.append({
                'index': i,
                'errors': serializer.errors
            })
    
    return Response({
        'created_count': len(created_messages),
        'error_count': len(errors),
        'created_messages': created_messages,
        'errors': errors
    }, status=status.HTTP_201_CREATED if created_messages else status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_handler(request):
    """
    Główny endpoint smartCARS API - kompatybilność z smartCARS 3
    Zwraca informacje o dostępnych endpointach w formacie smartCARS
    """
    return Response({
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
            "phpvms_version": "7.0.0",
            "features": ["ACARS", "Position Reporting", "Flight Tracking", "Authentication"],
            "endpoints": {
                # Nowe JWT endpointy (rekomendowane)
                "jwt_login": "/api/auth/login",
                "jwt_refresh": "/api/auth/refresh",
                "jwt_messages": "/acars/api/messages",
                "jwt_ping": "/acars/api/ping",
                
                # Legacy endpoints dla kompatybilności
                "login": "/acars/api/login",
                "user": "/acars/api/user", 
                "schedules": "/acars/api/schedules",
                "aircraft": "/acars/api/aircraft",
                "airports": "/acars/api/airports",
                "webhook": "/acars/webhook"
            }
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def smartcars_login(request):
    # Zapisz request do debugowania (zawsze)
    add_debug_request(request)
    """
    Legacy endpoint logowania dla kompatybilności z smartCARS
    Obsługuje email/api_key (smartCARS format), username/password (fallback) oraz Basic Auth
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import authenticate, get_user_model
    import logging
    import base64
    
    # Bezpieczne wyciąganie danych z request
    def safe_get_from_data(key):
        try:
            if hasattr(request.data, 'get'):
                return request.data.get(key)
            elif hasattr(request.data, '__getitem__'):
                return request.data.get(key, None) if hasattr(request.data, 'get') else None
        except:
            return None
        return None
    
    # Sprawdź Basic Authentication
    basic_email = None
    basic_api_key = None
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Basic '):
        try:
            creds = base64.b64decode(auth_header.split(' ')[1]).decode('utf-8')
            if ':' in creds:
                basic_email, basic_api_key = creds.split(':', 1)
        except Exception:
            pass
    
    # DEBUG: Zwróć informacje o żądaniu jeśli parametr debug=1
    if request.GET.get('debug') == '1':
        try:
            extracted_fields = {
                "email": (safe_get_from_data('email') or 
                         safe_get_from_data('username') or 
                         safe_get_from_data('pilot_id') or
                         safe_get_from_data('user_id') or
                         safe_get_from_data('user') or
                         safe_get_from_data('login') or
                         basic_email),
                "api_key": (safe_get_from_data('api_key') or 
                           safe_get_from_data('password') or
                           safe_get_from_data('key') or
                           safe_get_from_data('token') or
                           safe_get_from_data('pass') or
                           safe_get_from_data('pwd') or
                           safe_get_from_data('secret') or
                           basic_api_key),
                "basic_auth_found": bool(basic_email and basic_api_key),
                "basic_email": basic_email,
                "basic_api_key": basic_api_key[:5] + "..." if basic_api_key else None
            }
            
            # Bezpieczne czytanie body
            safe_body = None
            try:
                safe_body = request.body.decode('utf-8', errors='ignore') if request.body else None
            except Exception:
                safe_body = "Unable to read body (already parsed by DRF)"
            
            return Response({
                "debug_info": {
                    "content_type": getattr(request, 'content_type', 'unknown'),
                    "method": request.method,
                    "POST_data": dict(request.POST),
                    "JSON_data": dict(request.data) if hasattr(request.data, 'items') else str(request.data),
                    "query_params": dict(request.GET),
                    "headers": {k: v for k, v in request.headers.items()},
                    "body": safe_body,
                    "extracted_fields": extracted_fields
                }
            })
        except Exception as e:
            # Bezpieczne czytanie body w exception handler
            safe_body = None
            try:
                safe_body = request.body.decode('utf-8', errors='ignore') if request.body else None
            except Exception:
                safe_body = "Unable to read body (already parsed by DRF)"
            
            return Response({
                "debug_error": str(e),
                "raw_body": safe_body,
                "auth_header": auth_header,
                "basic_auth_parsed": {"email": basic_email, "api_key": basic_api_key[:5] + "..." if basic_api_key else None}
            })
    
    User = get_user_model()
    
    # Pobierz dane logowania - sprawdź wszystkie możliwe nazwy pól + Basic Auth
    email = (safe_get_from_data('email') or 
             safe_get_from_data('username') or 
             safe_get_from_data('pilot_id') or
             safe_get_from_data('user_id') or
             safe_get_from_data('user') or        # Dodane dla smartCARS
             safe_get_from_data('login') or       # Możliwy wariant
             basic_email)
    
    api_key = (safe_get_from_data('api_key') or 
               safe_get_from_data('password') or
               safe_get_from_data('key') or
               safe_get_from_data('token') or
               safe_get_from_data('pass') or       # Dodane dla smartCARS
               safe_get_from_data('pwd') or        # Możliwy wariant  
               safe_get_from_data('secret') or     # Możliwy wariant
               basic_api_key)
    
    if not email or not api_key:
        return Response({
            "status": "error",
            "message": "Email and API key required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Sprawdź uwierzytelnienie - wspieraj SmartCARS API keys
    user = None
    try:
        # Najpierw znajdź użytkownika po email
        user = User.objects.get(email__iexact=email)
        
        # Sprawdź czy istnieje osobny SmartCARS API key
        try:
            from .models import SmartcarsProfile
            profile = SmartcarsProfile.objects.get(user=user, is_active=True)
            if profile.api_key == api_key:
                # Zalogowano przez SmartCARS API key - zaktualizuj last_used
                from django.utils import timezone
                profile.last_used = timezone.now()
                profile.save(update_fields=['last_used'])
            else:
                user = None
        except SmartcarsProfile.DoesNotExist:
            # Fallback - sprawdź czy api_key to hasło użytkownika (dla kompatybilności)
            if not user.check_password(api_key):
                user = None
    except User.DoesNotExist:
        # Fallback - spróbuj standardowego authenticate (username zamiast email)
        user = authenticate(username=email, password=api_key)
    
    if user and user.is_active:
        # Generuj tokeny JWT
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            "status": "success",
            "message": "Login successful",
            "data": {
                "pilot_id": user.id,
                "api_key": str(refresh.access_token),  # JWT token jako API key
                "refresh_token": str(refresh),
                "user": {
                    "name": user.get_full_name() or user.username,
                    "email": user.email,
                }
            }
        }
        # Zapisz response do debugowania
        add_debug_request(request, response_data)
        return Response(response_data)
    else:
        error_response = {
            "status": "error", 
            "message": "Invalid credentials"
        }
        # Zapisz error response do debugowania
        add_debug_request(request, error_response)
        return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_user_v3(request):
    """
    Legacy endpoint informacji o użytkowniku dla kompatybilności z smartCARS
    Wymaga Bearer token w headerze Authorization lub api_key w parametrach
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
    # Sprawdź JWT token w header lub api_key parameter
    api_key = request.GET.get('api_key')
    
    if api_key and not request.META.get('HTTP_AUTHORIZATION'):
        # Dodaj Bearer token do headerów jeśli podano api_key
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {api_key}'
    
    # Manualnie uwierzytelniaj używając JWT
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if user_auth:
            user, token = user_auth
            request.user = user
        else:
            return Response({
                "status": "error",
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        return Response({
            "status": "error",
            "message": "Invalid token"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    return Response({
        "status": "success",
        "data": {
            "id": request.user.id,
            "name": request.user.get_full_name() or request.user.username,
            "email": request.user.email,
            "username": request.user.username,
            "country": "PL",  # Domyślnie Polska
            "curr_airport_id": "EPWA",  # Domyślnie Warszawa
            "total_flights": ACARSMessage.objects.filter(user=request.user).count(),
            "total_hours": 0,  # Można dodać kalkulację z czasu lotów
        }
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_basic_endpoint(request, endpoint_name):
    """
    Podstawowe endpointy (airports, aircraft, schedules) dla kompatybilności
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
    # Sprawdź JWT token w header lub api_key parameter
    api_key = request.GET.get('api_key')
    
    if api_key and not request.META.get('HTTP_AUTHORIZATION'):
        # Dodaj Bearer token do headerów jeśli podano api_key
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {api_key}'
    
    # Manualnie uwierzytelniaj używając JWT
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if user_auth:
            user, token = user_auth
            request.user = user
        else:
            return Response({
                "status": "error",
                "message": "Authentication required"
            }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception:
        return Response({
            "status": "error",
            "message": "Invalid token"
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Przykładowe dane - można rozszerzyć o prawdziwe dane z bazy
    if endpoint_name == "airports":
        data = [
            {"icao": "EPWA", "name": "Warsaw Chopin Airport", "country": "Poland"},
            {"icao": "EGLL", "name": "London Heathrow", "country": "United Kingdom"},
            {"icao": "EDDF", "name": "Frankfurt am Main", "country": "Germany"},
        ]
    elif endpoint_name == "aircraft": 
        data = [
            {"icao": "B738", "name": "Boeing 737-800", "registration": "SP-ABC"},
            {"icao": "A320", "name": "Airbus A320", "registration": "SP-DEF"},
        ]
    elif endpoint_name == "schedules":
        data = [
            {"flight_number": "TS001", "route": "EPWA-EGLL", "aircraft": "B738"},
            {"flight_number": "TS002", "route": "EGLL-EPWA", "aircraft": "A320"},
        ]
    else:
        return Response({
            "status": "error",
            "message": f"Unknown endpoint: {endpoint_name}"
        }, status=status.HTTP_404_NOT_FOUND)
    
    return Response({
        "status": "success",
        "data": data
    })

# ============================================================================
# OFFICIAL SMARTCARS 3 API IMPLEMENTATION
# Based on invernyx/smartcars-3-phpvms7-api official module
# ============================================================================

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def smartcars_api_handler(request):
    """
    Official smartCARS 3 API Handler - Main Entry Point
    Compatible with TFDi Design smartCARS 3 application
    Format based on official phpVMS 7 module: github.com/invernyx/smartcars-3-phpvms7-api
    """
    return Response({
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


@api_view(['POST'])
@permission_classes([AllowAny])
@parser_classes([FormParser, JSONParser])
def smartcars_login_v3(request):
    """
    Official smartCARS 3 Login Endpoint
    Supports email/api_key authentication (Discord/VATSIM SSO compatible)
    Returns session token for subsequent API calls
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import authenticate
    
    User = get_user_model()
    
    # Extract credentials - smartCARS 3 uses email/api_key format
    email = request.data.get('email') or request.data.get('username')
    api_key = request.data.get('api_key') or request.data.get('password')
    
    if not email or not api_key:
        return Response({
            "message": "Email and API key are required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Authenticate user
    user = None
    try:
        # Try to find user by email first
        user = User.objects.get(email__iexact=email)
        if not user.check_password(api_key):
            user = None
    except User.DoesNotExist:
        # Fallback to username authentication
        user = authenticate(username=email, password=api_key)
    
    if user and user.is_active:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "pilot_id": user.id,
            "session": str(refresh.access_token),  # Session token for API calls
            "name": user.get_full_name() or user.username,
            "email": user.email,
            "country": "PL",  # Default country
            "timezone": "Europe/Warsaw",
            "opt_in": True,
            "status": 1  # Active status
        })
    else:
        return Response({
            "message": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_user(request):
    """
    Official smartCARS 3 User Info Endpoint
    Returns user information for authenticated session
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
    # Extract session token from Authorization header or session parameter
    session_token = request.GET.get('session')
    if session_token and not request.META.get('HTTP_AUTHORIZATION'):
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {session_token}'
    
    # Authenticate using JWT
    jwt_auth = JWTAuthentication()
    try:
        user_auth = jwt_auth.authenticate(request)
        if user_auth:
            user, token = user_auth
            
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
    except Exception as e:
        return Response({
            "message": "Invalid session token"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_schedules(request):
    """
    Official smartCARS 3 Schedules Endpoint
    Returns available flight schedules for the virtual airline
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
def smartcars_aircraft(request):
    """
    Official smartCARS 3 Aircraft Endpoint
    Returns available aircraft for the virtual airline
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
def smartcars_airports(request):
    """
    Official smartCARS 3 Airports Endpoint
    Returns available airports for the virtual airline
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
def smartcars_bid(request):
    """
    Official smartCARS 3 Bid Endpoint
    Allows pilots to bid on flights
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
def smartcars_position(request):
    """
    Official smartCARS 3 Position Reporting Endpoint
    Receives and stores aircraft position data during flight
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
            serializer.save(user=user)
            
            return Response({
                "message": "Position updated successfully",
                "id": serializer.instance.id
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
def smartcars_pirep(request):
    """
    Official smartCARS 3 PIREP (Pilot Report) Endpoint
    Receives and processes completed flight reports
    """
    from rest_framework_simplejwt.authentication import JWTAuthentication
    
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
            serializer.save(user=user)
            
            return Response({
                "pirep_id": serializer.instance.id,
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