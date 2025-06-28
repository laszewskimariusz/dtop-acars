from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action, parser_classes
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from .models import ACARSMessage
from .serializers import ACARSMessageSerializer, ACARSMessageReadSerializer


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
    """
    Legacy endpoint logowania dla kompatybilności z smartCARS
    Obsługuje email/api_key (smartCARS format) oraz username/password (fallback)
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    from django.contrib.auth import authenticate, get_user_model
    import logging
    
    # DEBUG: Zwróć informacje o żądaniu jeśli parametr debug=1
    if request.GET.get('debug') == '1':
        try:
            return Response({
                "debug_info": {
                    "content_type": getattr(request, 'content_type', 'unknown'),
                    "method": request.method,
                    "POST_data": dict(request.POST),
                    "JSON_data": dict(request.data) if hasattr(request.data, 'items') else request.data,
                    "query_params": dict(request.GET),
                    "headers": {k: v for k, v in request.headers.items()},
                    "body": request.body.decode('utf-8', errors='ignore') if request.body else None,
                    "extracted_fields": {
                        "email": request.data.get('email') or request.data.get('username'),
                        "api_key": request.data.get('api_key') or request.data.get('password'),
                    }
                }
            })
        except Exception as e:
            return Response({
                "debug_error": str(e),
                "raw_body": request.body.decode('utf-8', errors='ignore') if request.body else None
            })
    
    User = get_user_model()
    
    # Pobierz dane logowania - sprawdź wszystkie możliwe nazwy pól
    email = (request.data.get('email') or 
             request.data.get('username') or 
             request.data.get('pilot_id') or
             request.data.get('user_id'))
    
    api_key = (request.data.get('api_key') or 
               request.data.get('password') or
               request.data.get('key') or
               request.data.get('token'))
    
    if not email or not api_key:
        return Response({
            "status": "error",
            "message": "Email and API key required"
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Sprawdź uwierzytelnienie - najpierw spróbuj przez email
    user = None
    try:
        user = User.objects.get(email__iexact=email)
        # Sprawdź czy api_key to hasło użytkownika (dla kompatybilności)
        if not user.check_password(api_key):
            user = None
    except User.DoesNotExist:
        # Fallback - spróbuj standardowego authenticate
        user = authenticate(username=email, password=api_key)
    
    if user and user.is_active:
        # Generuj tokeny JWT
        refresh = RefreshToken.for_user(user)
        
        return Response({
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
        })
    else:
        return Response({
            "status": "error", 
            "message": "Invalid credentials"
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([AllowAny])
def smartcars_user(request):
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