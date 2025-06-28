#!/usr/bin/env python3
"""
Test kompatybilności z smartCARS 3 od TFDi Design
"""

import requests
import json

def test_smartcars_handler():
    """Test głównego endpointu handlera"""
    print("🧪 Testowanie głównego handlera smartCARS...")
    
    urls = [
        "https://dtopsky.topsky.app/acars/api/",
        "https://dtopsky.topsky.app/acars/api"
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Handler: {data.get('handler', {}).get('name')}")
                print(f"Version: {data.get('handler', {}).get('version')}")
                print("Endpoints:", list(data.get('data', {}).get('endpoints', {}).keys()))
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    print()

def test_smartcars_login():
    """Test logowania smartCARS API"""
    print("🧪 Testowanie logowania smartCARS API...")
    
    urls = [
        "https://dtopsky.topsky.app/acars/api/login/",  # Poprawny URL z trailing slash
        "https://dtopsky.topsky.app/acars/login/"  # legacy
    ]
    
    credentials = {
        "email": "laszewskimariusz@gmail.com",  # smartCARS format: email/api_key
        "api_key": "nowe_haslo123"
    }
    
    for url in urls:
        try:
            response = requests.post(
                url,
                json=credentials,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            print(f"✅ {url} - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"  Login successful!")
                    print(f"  Pilot ID: {data.get('data', {}).get('pilot_id')}")
                    print(f"  API Key: {data.get('data', {}).get('api_key', 'MISSING')[:20]}...")
                    return data.get('data', {}).get('api_key')
                else:
                    print(f"  Login failed: {data.get('message')}")
            else:
                print(f"  HTTP Error: {response.text}")
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
    print()
    return None

def test_user_info(api_key):
    """Test endpointu informacji o użytkowniku"""
    if not api_key:
        print("❌ Brak API key, pomijam test user info")
        return
    
    print("🧪 Testowanie endpointu user info...")
    
    urls = [
        f"https://dtopsky.topsky.app/acars/api/user?api_key={api_key}",
        f"https://dtopsky.topsky.app/acars/user?api_key={api_key}"  # legacy
    ]
    
    for url in urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ {url[:50]}... - Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    user_data = data.get('data', {})
                    print(f"  User: {user_data.get('name')}")
                    print(f"  Email: {user_data.get('email')}")
                    print(f"  Country: {user_data.get('country')}")
                    print(f"  Current Airport: {user_data.get('curr_airport_id')}")
                else:
                    print(f"  Error: {data.get('message')}")
            else:
                print(f"  HTTP Error: {response.text}")
        except Exception as e:
            print(f"❌ {url[:50]}... - Error: {e}")
    print()

def test_basic_endpoints(api_key):
    """Test podstawowych endpointów (airports, aircraft, schedules)"""
    if not api_key:
        print("❌ Brak API key, pomijam test endpointów")
        return
    
    endpoints = ['airports', 'aircraft', 'schedules']
    
    for endpoint in endpoints:
        print(f"🧪 Testowanie endpointu {endpoint}...")
        
        urls = [
            f"https://dtopsky.topsky.app/acars/api/{endpoint}?api_key={api_key}",
            f"https://dtopsky.topsky.app/acars/{endpoint}?api_key={api_key}"  # legacy
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=5)
                print(f"✅ {url[:60]}... - Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        items = data.get('data', [])
                        if isinstance(items, list):
                            print(f"  Znaleziono {len(items)} elementów")
                        elif isinstance(items, dict):
                            print(f"  Kategorie: {list(items.keys())}")
                    else:
                        print(f"  Error: {data.get('message')}")
                else:
                    print(f"  HTTP Error: {response.text}")
            except Exception as e:
                print(f"❌ {url[:60]}... - Error: {e}")
        print()

if __name__ == "__main__":
    print("🚀 Test kompatybilności smartCARS 3")
    print("=" * 60)
    
    # Test głównego handlera
    test_smartcars_handler()
    
    # Test logowania i pobranie API key
    api_key = test_smartcars_login()
    
    # Test pozostałych endpointów
    test_user_info(api_key)
    test_basic_endpoints(api_key)
    
    print("=" * 60)
    print("✅ Test zakończony!")
    
    if api_key:
        print(f"\n🔑 Twój API Key dla smartCARS:")
        print(f"   {api_key}")
        print("\n📋 URL do konfiguracji w smartCARS 3:")
        print("   https://dtopsky.topsky.app/acars/api/")
        print("   (Topsky Virtual Airlines)")
    else:
        print("\n❌ Logowanie nie powiodło się - sprawdź hasło użytkownika") 