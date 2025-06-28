#!/usr/bin/env python3
"""
Test logowania smartCARS bez trailing slash
"""

import requests
import json

def test_login_no_slash():
    """Test logowania na URL bez trailing slash"""
    print("🧪 Testowanie logowania bez trailing slash...")
    
    login_data = {
        "email": "laszewskimariusz@gmail.com",
        "api_key": "nowe_haslo123"
    }
    
    # Test URL bez slash (to jest to czego używa smartCARS)
    url = "https://dtopsky.topsky.app/acars/api/login"
    
    try:
        response = requests.post(
            url,
            json=login_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"✅ POST {url} - Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                print(f"  ✅ Login successful!")
                print(f"  Pilot ID: {data.get('data', {}).get('pilot_id')}")
                api_key = data.get('data', {}).get('api_key', '')
                print(f"  API Key: {api_key[:30]}...")
                return True
            else:
                print(f"  ❌ Login failed: {data.get('message')}")
        else:
            print(f"  ❌ HTTP Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Test logowania smartCARS bez trailing slash")
    print("=" * 60)
    
    success = test_login_no_slash()
    
    print("=" * 60)
    if success:
        print("✅ smartCARS powinien teraz działać bez problemu '301 - Redirects Are Not Allowed'!")
        print("\n📋 Użyj w smartCARS 3:")
        print("   URL: https://dtopsky.topsky.app/acars/api/")
        print("   Email: laszewskimariusz@gmail.com")
        print("   API Key: nowe_haslo123")
    else:
        print("❌ Problem nadal występuje") 