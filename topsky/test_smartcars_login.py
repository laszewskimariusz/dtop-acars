#!/usr/bin/env python3
"""
Test logowania smartCARS z email i api_key (hasłem)
"""

import requests
import json

def test_smartcars_login_with_email():
    """Test logowania smartCARS z email/password jako api_key"""
    print("🧪 Testowanie logowania smartCARS z email/password...")
    
    login_data = {
        "email": "laszewskimariusz@gmail.com",  # prawdziwy email użytkownika Zatto
        "api_key": "nowe_haslo123"  # hasło jako api_key
    }
    
    url = "https://dtopsky.topsky.app/acars/api/login/"
    
    try:
        # Test JSON
        response = requests.post(
            url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"✅ POST {url} (JSON) - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"  ✅ Login successful!")
                print(f"  Pilot ID: {data.get('data', {}).get('pilot_id')}")
                api_key = data.get('data', {}).get('api_key', '')
                print(f"  API Key: {api_key[:20]}...")
                return api_key
            else:
                print(f"  ❌ Login failed: {data.get('message')}")
                print(f"  Response: {response.text}")
        else:
            print(f"  ❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"❌ JSON test error: {e}")
    
    try:
        # Test form-data
        response = requests.post(
            url,
            data=login_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=10
        )
        print(f"✅ POST {url} (form-data) - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"  ✅ Login successful!")
                print(f"  Pilot ID: {data.get('data', {}).get('pilot_id')}")
                api_key = data.get('data', {}).get('api_key', '')
                print(f"  API Key: {api_key[:20]}...")
                return api_key
            else:
                print(f"  ❌ Login failed: {data.get('message')}")
                print(f"  Response: {response.text}")
        else:
            print(f"  ❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"❌ Form-data test error: {e}")
    
    return None

def test_legacy_username_password():
    """Test fallback z username/password"""
    print("\n🧪 Testowanie fallback username/password...")
    
    login_data = {
        "username": "Zatto",
        "password": "nowe_haslo123"
    }
    
    url = "https://dtopsky.topsky.app/acars/api/login/"
    
    try:
        response = requests.post(
            url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"✅ POST {url} (username/password) - Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"  ✅ Fallback login successful!")
                api_key = data.get('data', {}).get('api_key', '')
                print(f"  API Key: {api_key[:20]}...")
                return api_key
            else:
                print(f"  ❌ Login failed: {data.get('message')}")
        else:
            print(f"  ❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    print("🚀 Test logowania smartCARS")
    print("=" * 60)
    
    # Test głównych formatów smartCARS
    api_key = test_smartcars_login_with_email()
    
    # Test fallback
    if not api_key:
        api_key = test_legacy_username_password()
    
    print("=" * 60)
    if api_key:
        print("✅ Logowanie powiodło się!")
        print(f"🔑 API Key: {api_key}")
    else:
        print("❌ Logowanie nie powiodło się!") 