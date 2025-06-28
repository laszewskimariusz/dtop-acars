#!/usr/bin/env python3
"""
Test Oficjalnego smartCARS 3 API
Zgodny z oficjalnym phpVMS 7 module od TFDi Design
URL: /api/smartcars/
"""

import requests
import json
import time

# Konfiguracja
BASE_URL = "http://127.0.0.1:8000/api/smartcars"
PRODUCTION_URL = "https://dtopsky.topsky.app/api/smartcars"

# Dane testowe
TEST_CREDENTIALS = {
    "email": "laszewskimariusz@gmail.com",
    "api_key": "nowe_haslo123"
}

def test_handler():
    """Test głównego handlera API"""
    print("🧪 Testowanie oficjalnego smartCARS 3 Handler...")
    
    urls = [BASE_URL, f"{BASE_URL}/"]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Handler: {data.get('handler', {}).get('name')}")
                print(f"  Version: {data.get('handler', {}).get('version')}")
                print(f"  phpVMS: {data.get('phpvms', {}).get('version')}")
                print(f"  Auth: {data.get('auth')}")
            else:
                print(f"  Błąd: {response.text}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    print()

def test_login():
    """Test logowania smartCARS 3"""
    print("🧪 Testowanie logowania smartCARS 3...")
    
    urls = [f"{BASE_URL}/login", f"{BASE_URL}/login/"]
    
    session_token = None
    
    for url in urls:
        try:
            response = requests.post(
                url,
                json=TEST_CREDENTIALS,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            print(f"✅ {url} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Login successful!")
                print(f"  Pilot ID: {data.get('pilot_id')}")
                print(f"  Name: {data.get('name')}")
                print(f"  Email: {data.get('email')}")
                print(f"  Country: {data.get('country')}")
                print(f"  Session: {data.get('session', 'MISSING')[:20]}...")
                session_token = data.get('session')
                break
            else:
                print(f"  Login failed: {response.text}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    
    print()
    return session_token

def test_user_info(session_token):
    """Test endpointu informacji o użytkowniku"""
    if not session_token:
        print("❌ Brak session token - pomijanie test user info")
        return
    
    print("🧪 Testowanie informacji o użytkowniku...")
    
    urls = [f"{BASE_URL}/user", f"{BASE_URL}/user/"]
    
    for url in urls:
        try:
            # Test z session parameter
            response = requests.get(
                f"{url}?session={session_token}",
                timeout=5
            )
            print(f"✅ {url}?session=... - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  Pilot ID: {data.get('pilot_id')}")
                print(f"  Name: {data.get('name')}")
                print(f"  Total flights: {data.get('total_flights')}")
                print(f"  Current airport: {data.get('curr_airport_id')}")
                break
            else:
                print(f"  Błąd: {response.text}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    print()

def test_data_endpoints(session_token):
    """Test endpointów danych (schedules, aircraft, airports)"""
    if not session_token:
        print("❌ Brak session token - pomijanie test data endpoints")
        return
    
    print("🧪 Testowanie endpointów danych...")
    
    endpoints = ['schedules', 'aircraft', 'airports']
    
    for endpoint in endpoints:
        try:
            url = f"{BASE_URL}/{endpoint}?session={session_token}"
            response = requests.get(url, timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  Zwrócono {len(data)} rekordów")
                    if data:
                        print(f"  Przykład: {json.dumps(data[0], indent=2)[:100]}...")
                else:
                    print(f"  Data: {data}")
            else:
                print(f"  Błąd: {response.text}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {e}")
    print()

def test_bid_flight(session_token):
    """Test bidowania na lot"""
    if not session_token:
        print("❌ Brak session token - pomijanie test bid")
        return
    
    print("🧪 Testowanie bidowania na lot...")
    
    bid_data = {
        "session": session_token,
        "flight_id": 1,
        "aircraft_id": 1
    }
    
    try:
        url = f"{BASE_URL}/bid"
        response = requests.post(
            url,
            json=bid_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"✅ bid - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Bid created: {data.get('message')}")
            print(f"  Bid ID: {data.get('bid', {}).get('id')}")
        else:
            print(f"  Błąd: {response.text}")
    except Exception as e:
        print(f"❌ bid - Error: {e}")
    print()

def test_position_report(session_token):
    """Test raportowania pozycji"""
    if not session_token:
        print("❌ Brak session token - pomijanie test position")
        return
    
    print("🧪 Testowanie raportowania pozycji...")
    
    position_data = {
        "session": session_token,
        "lat": 52.1656900,
        "lng": 20.9670900,
        "altitude": 35000,
        "heading": 90,
        "speed": 450,
        "aircraft": "B738",
        "flight_number": "TS001"
    }
    
    try:
        url = f"{BASE_URL}/position"
        response = requests.post(
            url,
            json=position_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"✅ position - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Position updated: {data.get('message')}")
            print(f"  Record ID: {data.get('id')}")
        else:
            print(f"  Błąd: {response.text}")
    except Exception as e:
        print(f"❌ position - Error: {e}")
    print()

def test_production():
    """Test na serwerze produkcyjnym"""
    print("🌐 Testowanie na serwerze produkcyjnym...")
    
    try:
        response = requests.get(PRODUCTION_URL, timeout=10)
        print(f"✅ Production URL - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Handler: {data.get('handler', {}).get('name')}")
            print(f"  Version: {data.get('handler', {}).get('version')}")
        else:
            print(f"  Błąd: {response.text}")
    except Exception as e:
        print(f"❌ Production test - Error: {e}")
    print()

if __name__ == "__main__":
    print("🚀 Test oficjalnego smartCARS 3 API")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Production URL: {PRODUCTION_URL}")
    print("=" * 60)
    
    # Test głównego handlera
    test_handler()
    
    # Test logowania i pobranie session token
    session_token = test_login()
    
    # Test informacji o użytkowniku
    test_user_info(session_token)
    
    # Test endpointów danych
    test_data_endpoints(session_token)
    
    # Test bidowania na lot
    test_bid_flight(session_token)
    
    # Test raportowania pozycji
    test_position_report(session_token)
    
    # Test na produkcji
    test_production()
    
    print("=" * 60)
    print("✅ Test zakończony!")
    print()
    
    if session_token:
        print("🔧 Konfiguracja dla smartCARS 3:")
        print(f"Script URL: {PRODUCTION_URL}")
        print(f"Email: {TEST_CREDENTIALS['email']}")
        print(f"API Key: {TEST_CREDENTIALS['api_key']}")
        print()
        print("📱 URL dla aplikacji smartCARS 3:")
        print("https://dtopsky.topsky.app/api/smartcars/")
        print("(Topsky Virtual Airlines)")
    else:
        print("❌ Nie udało się zalogować - sprawdź dane logowania") 