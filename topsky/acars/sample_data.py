"""
Przykładowe dane testowe dla systemu ACARS
Użyj tego skryptu do wygenerowania testowych komunikatów w systemie
"""

from django.contrib.auth.models import User
from .models import ACARSMessage
from datetime import datetime, time
from decimal import Decimal

def create_sample_data():
    """Tworzy przykładowe dane testowe ACARS"""
    
    # Sprawdź czy istnieje użytkownik testowy
    test_user, created = User.objects.get_or_create(
        username='pilot_test',
        defaults={
            'email': 'pilot@example.com',
            'first_name': 'Jan',
            'last_name': 'Kowalski'
        }
    )
    
    if created:
        test_user.set_password('testpass123')
        test_user.save()
        print(f"Utworzono użytkownika testowego: {test_user.username}")
    
    # Przykładowe komunikaty ACARS
    sample_messages = [
        {
            'aircraft_id': 'SP-LOT',
            'flight_number': 'LO123',
            'route': 'WAW-JFK',
            'direction': 'OUT',
            'latitude': Decimal('52.165726'),
            'longitude': Decimal('20.967130'),
            'altitude': 35000,
            'speed': 480,
            'heading': 270,
            'fuel_on_board': Decimal('18500.50'),
            'pax_count': 180,
            'payload': {
                'type': 'departure',
                'gate': 'A12',
                'fuel_on_board': 18500.50,
                'passengers': 180,
                'departure_time': '14:30',
                'estimated_flight_time': '08:45'
            }
        },
        {
            'aircraft_id': 'SP-LOT',
            'flight_number': 'LO123',
            'route': 'WAW-JFK',
            'direction': 'OUT',
            'latitude': Decimal('55.123456'),
            'longitude': Decimal('15.654321'),
            'altitude': 37000,
            'speed': 485,
            'heading': 275,
            'fuel_on_board': Decimal('16200.25'),
            'engine_n1': Decimal('92.5'),
            'fuel_flow': Decimal('2400.00'),
            'temperature_oat': Decimal('-45.5'),
            'payload': {
                'type': 'position_report',
                'fuel_remaining': 16200.25,
                'speed': 485,
                'heading': 275,
                'estimated_arrival': '22:15',
                'weather': 'Clear'
            }
        },
        {
            'aircraft_id': 'SP-LVA',
            'flight_number': 'LO456',
            'route': 'KRK-LHR',
            'direction': 'IN',
            'latitude': Decimal('51.4700'),
            'longitude': Decimal('-0.4543'),
            'altitude': 12000,
            'speed': 320,
            'heading': 90,
            'fuel_on_board': Decimal('4500.75'),
            'pax_count': 156,
            'time_on': time(16, 45),
            'payload': {
                'type': 'arrival',
                'gate': 'B7',
                'fuel_remaining': 4500.75,
                'flight_time': '02:15',
                'passengers_disembarking': 156,
                'gate_arrival_time': '16:45'
            }
        },
        {
            'aircraft_id': 'SP-LRA',
            'flight_number': 'LO789',
            'route': 'GDN-MUC',
            'direction': 'OUT',
            'latitude': Decimal('54.377560'),
            'longitude': Decimal('18.466222'),
            'altitude': 5000,
            'speed': 250,
            'heading': 180,
            'fuel_on_board': Decimal('8900.00'),
            'engine_n1': Decimal('85.2'),
            'fuel_flow': Decimal('1800.00'),
            'maintenance_code': 'A001',
            'payload': {
                'type': 'maintenance_report',
                'maintenance_code': 'A001',
                'description': 'Scheduled inspection completed',
                'next_inspection': '2025-07-15',
                'status': 'OK'
            }
        },
        {
            'aircraft_id': 'SP-LRB',
            'flight_number': 'LO999',
            'route': 'WRO-CDG',
            'direction': 'OUT',
            'latitude': Decimal('51.102683'),
            'longitude': Decimal('17.085833'),
            'altitude': 28000,
            'speed': 470,
            'heading': 250,
            'fuel_on_board': Decimal('12800.30'),
            'engine_n1': Decimal('88.7'),
            'engine_epr': Decimal('1.85'),
            'fuel_flow': Decimal('2200.00'),
            'temperature_oat': Decimal('-32.1'),
            'wind_info': '250/35',
            'cost_index': 85,
            'payload': {
                'type': 'cruise_report',
                'altitude': 28000,
                'speed': 470,
                'fuel_flow': 2200,
                'wind': '250/35',
                'temperature': -32.1,
                'eta': '18:30'
            }
        }
    ]
    
    # Tworzenie komunikatów
    created_count = 0
    for msg_data in sample_messages:
        message, created = ACARSMessage.objects.get_or_create(
            user=test_user,
            aircraft_id=msg_data['aircraft_id'],
            flight_number=msg_data['flight_number'],
            payload=msg_data['payload'],
            defaults=msg_data
        )
        
        if created:
            created_count += 1
            print(f"Utworzono komunikat: {message}")
    
    print(f"\nPomyślnie utworzono {created_count} komunikatów testowych ACARS")
    print(f"Dane logowania: username='pilot_test', password='testpass123'")
    print(f"Dashboard ACARS: http://127.0.0.1:8000/acars/")
    
    return created_count

# Funkcja do użycia w Django shell
def load_sample_data():
    """
    Funkcja do wywołania w Django shell:
    python manage.py shell
    >>> from acars.sample_data import load_sample_data
    >>> load_sample_data()
    """
    return create_sample_data()

if __name__ == "__main__":
    print("Ten skrypt musi być uruchomiony w kontekście Django.")
    print("Użyj: python manage.py shell")
    print(">>> from acars.sample_data import load_sample_data")
    print(">>> load_sample_data()") 