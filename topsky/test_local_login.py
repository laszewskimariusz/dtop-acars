#!/usr/bin/env python3
"""
Test lokalny logowania smartCARS
"""

import requests
import json

def test_local_login():
    """Test logowania na lokalnym serwerze"""
    print("🧪 Testowanie lokalnego logowania smartCARS...")
    
    # Dane do testów
    test_cases = [
        {
            "name": "email/api_key format (Zatto user)",
            "data": {"email": "laszewskimariusz@gmail.com", "api_key": "nowe_haslo123"}
        },
        {
            "name": "username/password format (Zatto user)", 
            "data": {"username": "Zatto", "password": "nowe_haslo123"}
        },
        {
            "name": "email/api_key format (test user)",
            "data": {"email": "test@example.com", "api_key": "testpassword"}
        }
    ]
    
    url = "http://127.0.0.1:8000/acars/api/login/"
    
    for test_case in test_cases:
        print(f"\n📝 Test: {test_case['name']}")
        
        try:
            # Test JSON
            response = requests.post(
                url,
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            print(f"  JSON - Status: {response.status_code}")
            if response.content:
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"  Raw: {response.text}")
        except Exception as e:
            print(f"  ❌ JSON Error: {e}")
        
        try:
            # Test form-data
            response = requests.post(
                url,
                data=test_case['data'],
                timeout=5
            )
            print(f"  Form - Status: {response.status_code}")
            if response.content:
                try:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)}")
                except:
                    print(f"  Raw: {response.text}")
        except Exception as e:
            print(f"  ❌ Form Error: {e}")

if __name__ == "__main__":
    print("🚀 Test lokalny smartCARS logowania")
    print("=" * 60)
    print("⚠️  Upewnij się, że serwer działa: python manage.py runserver")
    print("=" * 60)
    
    test_local_login() 