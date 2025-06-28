#!/usr/bin/env python3
"""
Test różnych formatów na produkcji
"""

import requests
import json

def test_production_endpoints():
    """Test różnych endpointów na produkcji"""
    print("🧪 Test endpointów produkcyjnych")
    
    base_url = "https://dtopsky.topsky.app"
    username = "laszewskimariusz@gmail.com"
    password = "nowe_haslo123"
    
    endpoints_to_test = [
        # Nasze obecne endpointy
        "/api/smartcars/login",
        "/acars/api/login",
        
        # Potencjalne endpointy zgodne z phpVMS format
        "/api/1.0.2/pilot/login",
        "/api/pilot/login", 
        "/api/phpvms7/pilot/login",
    ]
    
    for endpoint in endpoints_to_test:
        print(f"\n📍 Test: {endpoint}")
        
        # Test z username w GET, password w POST (SmartCARS format)
        full_url = f"{base_url}{endpoint}?username={username}"
        
        try:
            response = requests.post(
                full_url,
                json={"password": password},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    # Sprawdź format odpowiedzi
                    if 'session' in data:
                        print(f"   ✅ Ma 'session' token!")
                        if 'pilot_id' in data:
                            print(f"   ✅ Ma 'pilot_id': {data['pilot_id']}")
                        if 'message' in data:
                            print(f"   📄 Message: {data['message']}")
                    elif 'pilotID' in data:
                        print(f"   ✅ Ma 'pilotID': {data['pilotID']}")
                    else:
                        print(f"   ⚠️  Nieoczekiwany format: {list(data.keys())}")
                except json.JSONDecodeError:
                    print(f"   ❌ Nie JSON: {response.text[:100]}")
            elif response.status_code == 404:
                print(f"   ❌ Nie znaleziono")
            elif response.status_code == 400:
                try:
                    error = response.json()
                    print(f"   ❌ Error 400: {error.get('message', response.text)}")
                except:
                    print(f"   ❌ Error 400: {response.text[:100]}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text[:100]}")
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
    
    # Test głównych handlerów
    print(f"\n🌐 Test głównych handlerów:")
    handlers = [
        "/api/smartcars/",
        "/api/",
        "/api/1.0.2/",
    ]
    
    for handler in handlers:
        try:
            response = requests.get(f"{base_url}{handler}", timeout=5)
            print(f"   GET {handler} - Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'apiVersion' in data and 'handler' in data:
                        print(f"      ✅ SmartCARS format: v{data['apiVersion']}")
                    else:
                        print(f"      📄 Keys: {list(data.keys())}")
                except:
                    print(f"      ❌ Nie JSON")
        except Exception as e:
            print(f"      ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Test formatów produkcyjnych SmartCARS")
    print("=" * 60)
    test_production_endpoints()
    print("=" * 60)
    print("📝 Szukamy endpoint który zwraca session token bez błędów") 