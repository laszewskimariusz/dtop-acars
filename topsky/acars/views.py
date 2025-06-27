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
            "handlerName": "Django ACARS Handler",
            "handlerVersion": "1.0.0", 
            "handlerAuthor": "Django ACARS System",
            "handlerWebsite": "https://dtopsky.topsky.app",
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
