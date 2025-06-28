#!/usr/bin/env python3
"""
Debug logowania - sprawdź co dokładnie zwraca endpoint
"""

import requests
import json
import base64

def test_login_response():
    """Test dokładnej odpowiedzi logowania"""
    print("🧪 Debug odpowiedzi logowania")
    
    base_url = "http://localhost:8000"
    username = "laszewskimariusz@gmail.com"
    password = "nowe_haslo123"
    
    # Test 1: SmartCARS API login
    print("\n1️⃣ Test /api/smartcars/login:")
    url = f"{base_url}/api/smartcars/login?username={username}"
    
    try:
        response = requests.post(
            url,
            json={"password": password},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Odpowiedź JSON:")
            print(json.dumps(data, indent=2))
            
            # Sprawdź JWT token
            if 'session' in data:
                session_token = data['session']
                print(f"\n🔍 Analiza JWT token:")
                try:
                    # Dekoduj JWT (bez weryfikacji - tylko dla debugu)
                    parts = session_token.split('.')
                    if len(parts) == 3:
                        header = base64.b64decode(parts[0] + '==')  # padding
                        payload = base64.b64decode(parts[1] + '==')  # padding
                        
                        print(f"Header: {header.decode('utf-8')}")
                        print(f"Payload: {payload.decode('utf-8')}")
                    else:
                        print("❌ Nieprawidłowy format JWT")
                except Exception as e:
                    print(f"❌ Błąd dekodowania JWT: {e}")
        else:
            print(f"❌ Error response: {response.text}")
            
    except Exception as e:
        print(f"❌ Request error: {e}")
    
    # Test 2: Legacy format dla porównania
    print("\n2️⃣ Test legacy /acars/api/login:")
    url2 = f"{base_url}/acars/api/login/?username={username}"
    
    try:
        response = requests.post(
            url2,
            json={"password": password},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Odpowiedź JSON:")
            print(json.dumps(data, indent=2))
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_auth_header():
    """Test czy endpoint akceptuje Bearer token"""
    print("\n3️⃣ Test Bearer token authorization:")
    
    # Najpierw zaloguj się
    login_url = "http://localhost:8000/api/smartcars/login?username=laszewskimariusz@gmail.com"
    login_response = requests.post(login_url, json={"password": "nowe_haslo123"})
    
    if login_response.status_code == 200:
        session_token = login_response.json().get('session')
        print(f"Token otrzymany: {session_token[:30]}...")
        
        # Test user endpoint z Bearer token
        user_url = "http://localhost:8000/api/smartcars/user"
        headers = {'Authorization': f'Bearer {session_token}'}
        
        user_response = requests.get(user_url, headers=headers)
        print(f"User endpoint status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            print("✅ Bearer token działa!")
            print(json.dumps(user_response.json(), indent=2))
        else:
            print(f"❌ Bearer token nie działa: {user_response.text}")
    else:
        print("❌ Nie można się zalogować do testu Bearer token")

if __name__ == "__main__":
    test_login_response()
    test_auth_header() 