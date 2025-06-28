#!/usr/bin/env python3
"""
Skrypt testowy do sprawdzenia logowania smartcars
"""

import requests
import json
import sys

def test_smartcars_login():
    """Test logowania do smartcars API"""
    
    # URL endpointu
    login_url = "http://localhost:8000/acars/login"
    
    # Dane do logowania
    credentials = {
        "username": "Zatto",
        "password": "nowe_haslo123"
    }
    
    print("🧪 Testowanie logowania smartcars...")
    print(f"URL: {login_url}")
    print(f"Credentials: {credentials}")
    print("-" * 50)
    
    try:
        # Wysłanie żądania logowania
        response = requests.post(
            login_url,
            json=credentials,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Parsowanie odpowiedzi
        if response.content:
            try:
                data = response.json()
                print(f"Response JSON:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                
                if data.get('success'):
                    print("\n✅ SUKCES! Logowanie działa poprawnie")
                    print(f"Token: {data.get('data', {}).get('token', 'BRAK')}")
                else:
                    print("\n❌ BŁĄD! Logowanie nie powiodło się")
                    print(f"Komunikat: {data.get('message', 'Brak komunikatu')}")
                    
            except json.JSONDecodeError:
                print(f"Raw Response: {response.text}")
        else:
            print("Pusta odpowiedź")
            
    except requests.exceptions.ConnectionError:
        print("❌ BŁĄD! Nie można połączyć się z serwerem")
        print("Upewnij się, że serwer Django działa na localhost:8000")
        print("Uruchom: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ BŁĄD: {str(e)}")

def test_user_info():
    """Test endpointu informacji o użytkowniku"""
    
    # Najpierw pobierz token
    login_url = "http://localhost:8000/acars/login"
    credentials = {"username": "Zatto", "password": "nowe_haslo123"}
    
    try:
        login_response = requests.post(login_url, json=credentials)
        if login_response.status_code == 200:
            login_data = login_response.json()
            if login_data.get('success'):
                token = login_data['data']['token']
                
                # Test endpointu user info
                user_url = "http://localhost:8000/acars/user"
                headers = {'Authorization': f'Bearer {token}'}
                
                print("\n🧪 Testowanie endpointu user info...")
                print(f"URL: {user_url}")
                print(f"Token: {token}")
                
                user_response = requests.get(user_url, headers=headers)
                print(f"Status Code: {user_response.status_code}")
                
                if user_response.content:
                    user_data = user_response.json()
                    print("User Info Response:")
                    print(json.dumps(user_data, indent=2, ensure_ascii=False))
                    
    except Exception as e:
        print(f"❌ BŁĄD w user info: {str(e)}")

if __name__ == "__main__":
    print("🚀 Smartcars API Test")
    print("=" * 50)
    
    test_smartcars_login()
    test_user_info()
    
    print("\n" + "=" * 50)
    print("Test zakończony!") 