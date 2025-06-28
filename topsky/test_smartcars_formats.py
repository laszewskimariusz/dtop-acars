#!/usr/bin/env python3
"""
Test różnych formatów danych jakie smartCARS może wysyłać
"""

import requests
import json

def test_various_formats():
    """Test różnych kombinacji formatów danych"""
    print("🧪 Testowanie różnych formatów danych smartCARS...")
    
    base_url = "http://127.0.0.1:8000/acars/api/login"
    
    # Wszystkie możliwe kombinacje danych jakie smartCARS może wysyłać
    test_cases = [
        {
            "name": "JSON email/api_key",
            "data": {"email": "laszewskimariusz@gmail.com", "api_key": "nowe_haslo123"},
            "content_type": "application/json",
            "method": "json"
        },
        {
            "name": "Form email/api_key", 
            "data": {"email": "laszewskimariusz@gmail.com", "api_key": "nowe_haslo123"},
            "content_type": "application/x-www-form-urlencoded",
            "method": "form"
        },
        {
            "name": "JSON username/password",
            "data": {"username": "Zatto", "password": "nowe_haslo123"},
            "content_type": "application/json", 
            "method": "json"
        },
        {
            "name": "Form username/password",
            "data": {"username": "Zatto", "password": "nowe_haslo123"},
            "content_type": "application/x-www-form-urlencoded",
            "method": "form"
        },
        {
            "name": "JSON pilot_id/password (możliwy format smartCARS)",
            "data": {"pilot_id": "2", "password": "nowe_haslo123"},
            "content_type": "application/json",
            "method": "json"
        },
        {
            "name": "JSON user_id/api_key (możliwy format smartCARS)",
            "data": {"user_id": "2", "api_key": "nowe_haslo123"},
            "content_type": "application/json",
            "method": "json"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        
        try:
            if test_case['method'] == 'json':
                response = requests.post(
                    base_url,
                    json=test_case['data'],
                    headers={'Content-Type': test_case['content_type']},
                    timeout=5
                )
            else:  # form
                response = requests.post(
                    base_url,
                    data=test_case['data'],
                    headers={'Content-Type': test_case['content_type']},
                    timeout=5
                )
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    print(f"  ✅ SUCCESS - Pilot ID: {data.get('data', {}).get('pilot_id')}")
                else:
                    print(f"  ❌ FAILED: {data.get('message')}")
            else:
                print(f"  ❌ HTTP Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")

def test_debug_endpoint():
    """Test debug endpoint żeby zobaczyć co serwer otrzymuje"""
    print(f"\n🔍 Test debug endpoint...")
    
    url = "http://127.0.0.1:8000/acars/api/login?debug=1"
    test_data = {"email": "test@example.com", "api_key": "testpass"}
    
    try:
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print(f"  Status: {response.status_code}")
        if response.content:
            data = response.json()
            print(f"  Debug info:")
            print(json.dumps(data, indent=2))
    except Exception as e:
        print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Test formatów danych smartCARS")
    print("=" * 60)
    print("⚠️  Upewnij się, że serwer działa: python manage.py runserver")
    print("=" * 60)
    
    test_various_formats()
    test_debug_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Testy zakończone!") 