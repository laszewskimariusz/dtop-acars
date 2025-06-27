from rest_framework import serializers
from .models import ACARSMessage


class ACARSMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ACARSMessage
        fields = [
            'id', 'timestamp', 'direction',
            # Identyfikacja lotu
            'aircraft_id', 'flight_number', 'route',
            # Pozycja i ruch
            'latitude', 'longitude', 'altitude', 'speed', 'heading',
            # Czasy OOOI
            'time_off', 'time_on', 'estimated_over', 'estimated_ramp',
            # Parametry silników i paliwa
            'engine_n1', 'engine_epr', 'fuel_flow', 'fuel_on_board',
            # Stan systemów
            'maintenance_code', 'fault_report',
            # Warunki pogodowe
            'temperature_oat', 'wind_info',
            # Pasażerowie i ładunek
            'pax_count', 'load_weight',
            # Operacje
            'cost_index', 'center_of_gravity',
            # Komunikacja
            'transmission_mode', 'label', 'msg_number',
            # Surowe dane
            'payload'
        ]
        read_only_fields = ['id', 'timestamp']


class ACARSMessageCreateSerializer(serializers.ModelSerializer):
    """Uproszczony serializer do tworzenia wiadomości - wymagane tylko podstawowe pola"""
    class Meta:
        model = ACARSMessage
        fields = [
            'aircraft_id', 'flight_number', 'direction', 'payload',
            'route', 'latitude', 'longitude', 'altitude'
        ] 