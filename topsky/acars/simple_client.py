"""
Prosty klient do testowania endpointu ACARS dla Smartcars
"""

import requests
import json

def send_acars_message(url, message_data):
    """
    Wysyła komunikat ACARS do endpointu
    
    Args:
        url (str): URL endpointu (np. https://dtopsky.topsky.app/acars/webhook/)
        message_data (dict): Dane komunikatu ACARS
    
    Returns:
        dict: Odpowiedź serwera
    """
    try:
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Smartcars-ACARS/1.0'
        }
        
        response = requests.post(url, json=message_data, headers=headers)
        
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else {},
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'status_code': 0,
            'response': {'error': str(e)},
            'success': False
        }

def test_endpoint(url):
    """
    Testuje czy endpoint odpowiada
    """
    try:
        response = requests.get(url)
        return {
            'status_code': response.status_code,
            'response': response.json() if response.content else {},
            'success': response.status_code == 200
        }
    except Exception as e:
        return {
            'status_code': 0,
            'response': {'error': str(e)},
            'success': False
        }

# Przykładowe dane ACARS
sample_messages = [
    {
        'aircraft_id': 'SP-LOT',
        'flight_number': 'LO123',
        'route': 'WAW-JFK',
        'latitude': 52.165726,
        'longitude': 20.967130,
        'altitude': 35000,
        'speed': 480,
        'heading': 270,
        'fuel_on_board': 18500.50,
        'pax_count': 180,
        'acars_type': 'departure',
        'gate': 'A12',
        'departure_time': '14:30'
    },
    {
        'aircraft_id': 'SP-LOT', 
        'flight_number': 'LO123',
        'route': 'WAW-JFK',
        'latitude': 55.123456,
        'longitude': 15.654321,
        'altitude': 37000,
        'speed': 485,
        'heading': 275,
        'fuel_on_board': 16200.25,
        'acars_type': 'position_report',
        'weather': 'Clear'
    }
]

if __name__ == "__main__":
    # Test dla lokalnego środowiska
    local_url = "http://127.0.0.1:8000/acars/webhook/"
    
    # Test dla produkcji
    prod_url = "https://dtopsky.topsky.app/acars/webhook/"
    
    print("Testing ACARS webhook endpoints...")
    
    # Testuj endpoint
    print(f"\n1. Testing GET {prod_url}")
    result = test_endpoint(prod_url)
    print(f"Status: {result['status_code']}, Response: {result['response']}")
    
    # Wyślij testowy komunikat
    print(f"\n2. Sending test message to {prod_url}")
    result = send_acars_message(prod_url, sample_messages[0])
    print(f"Status: {result['status_code']}, Response: {result['response']}") 