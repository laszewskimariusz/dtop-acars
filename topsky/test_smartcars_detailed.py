#!/usr/bin/env python3
import requests
import json

def test_smartcars_login_variations():
    """Test różnych sposobów logowania jakie smartCARS 3 może używać"""
    
    base_url = "https://dtopsky.topsky.app"
    credentials = {
        'username': 'Zatto',
        'password': 'nowe_haslo123'
    }
    
    print("🚀 Szczegółowy test logowania smartCARS 3")
    print("=" * 60)
    
    # Test 1: POST z application/x-www-form-urlencoded
    print("\n📋 Test 1: Form data (application/x-www-form-urlencoded)")
    try:
        response = requests.post(
            f"{base_url}/acars/api/login",
            data=credentials,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'smartCARS/3.0',
                'Accept': 'application/json'
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    # Test 2: POST z JSON
    print("\n📋 Test 2: JSON data (application/json)")
    try:
        response = requests.post(
            f"{base_url}/acars/api/login",
            json=credentials,
            headers={
                'User-Agent': 'smartCARS/3.0',
                'Accept': 'application/json'
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    # Test 3: Różne warianty nazw pól
    print("\n📋 Test 3: Różne nazwy pól (email, pilot_id)")
    test_variations = [
        {'email': 'Zatto', 'password': 'nowe_haslo123'},
        {'pilot_id': 'Zatto', 'password': 'nowe_haslo123'},
        {'email': 'laszewskimariusz@gmail.com', 'password': 'nowe_haslo123'},
    ]
    
    for i, creds in enumerate(test_variations):
        print(f"\n  Wariant {i+1}: {list(creds.keys())}")
        try:
            response = requests.post(
                f"{base_url}/acars/api/login",
                data=creds,
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'smartCARS/3.0'
                },
                timeout=10
            )
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Sukces! API Key: {data.get('data', {}).get('api_key', 'N/A')[:20]}...")
            else:
                print(f"  Response: {response.text[:200]}")
        except Exception as e:
            print(f"  ❌ Błąd: {e}")
    
    # Test 4: Sprawdź endpoint handler
    print("\n📋 Test 4: Handler endpoint")
    try:
        response = requests.get(
            f"{base_url}/acars/api/",
            headers={'User-Agent': 'smartCARS/3.0'},
            timeout=10
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Handler: {data.get('handler', {}).get('name')}")
            print(f"Endpoints: {data.get('response', {}).get('endpoints', [])}")
        else:
            print(f"Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    
    # Test 5: Sprawdź SSL i certyfikaty
    print("\n📋 Test 5: Sprawdzenie SSL")
    try:
        response = requests.get(
            f"{base_url}/acars/api/",
            verify=True,  # Sprawdź certyfikat SSL
            timeout=10
        )
        print(f"✅ SSL OK - Status: {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"❌ Problem SSL: {e}")
    except Exception as e:
        print(f"❌ Inny błąd: {e}")

if __name__ == "__main__":
    test_smartcars_login_variations() 