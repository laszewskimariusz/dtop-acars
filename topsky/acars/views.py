from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ACARSMessage
from .serializers import ACARSMessageSerializer

# Create your views here.

def acars_dashboard(request):
    """Renderuje stronę z interfejsem ACARS"""
    return render(request, 'acars/dashboard.html')

class ACARSMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ACARSMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Return only messages for the authenticated user
        return ACARSMessage.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
