#!/usr/bin/env python3
"""
Test szczegółowy produkcji - dokładnie co zwraca endpoint
"""

import requests
import json
import base64

def test_production_acars_login():
    """Test szczegółowy /acars/api/login na produkcji"""
    print("🧪 Test szczegółowy produkcji")
    
    base_url = "https://dtopsky.topsky.app"
    username = "laszewskimariusz@gmail.com"
    password = "nowe_haslo123"
    
    # Test SmartCARS format na produkcji
    print("\n1️⃣ Test SmartCARS format na /acars/api/login:")
    url = f"{base_url}/acars/api/login?username={username}"
    
    try:
        response = requests.post(
            url,
            json={"password": password},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n📄 Pełna odpowiedź JSON:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Analiza formatów
            has_session = 'session' in data
            has_pilot_id = 'pilot_id' in data or 'pilotID' in data
            has_message = 'message' in data
            has_status = 'status' in data
            
            print(f"\n🔍 Analiza formatu:")
            print(f"   session: {'✅' if has_session else '❌'}")
            print(f"   pilot_id/pilotID: {'✅' if has_pilot_id else '❌'}")
            print(f"   message: {'✅' if has_message else '❌'}")
            print(f"   status: {'✅' if has_status else '❌'}")
            
            # Sprawdź typ odpowiedzi
            if has_session and not has_status:
                print(f"   🎯 Format: SmartCARS (flat JSON)")
            elif has_status and data.get('status') == 'success':
                print(f"   🎯 Format: Django (nested JSON)")
            else:
                print(f"   ⚠️  Format: nieznany")
            
            # Sprawdź JWT token
            if has_session:
                session_token = data.get('session')
                print(f"\n🔍 Analiza JWT:")
                try:
                    parts = session_token.split('.')
                    if len(parts) == 3:
                        # Dodaj padding jeśli potrzebne
                        payload_b64 = parts[1]
                        padding = '=' * (4 - len(payload_b64) % 4)
                        payload = base64.b64decode(payload_b64 + padding)
                        payload_json = json.loads(payload.decode('utf-8'))
                        
                        print(f"   Payload: {json.dumps(payload_json, indent=4)}")
                        
                        # Sprawdź kluczowe pola dla SmartCARS
                        has_sub = 'sub' in payload_json
                        has_user_id = 'user_id' in payload_json
                        exp = payload_json.get('exp')
                        
                        print(f"   sub (pilot ID): {'✅' if has_sub else '❌'}")
                        print(f"   user_id: {'✅' if has_user_id else '❌'}")
                        print(f"   exp: {exp}")
                        
                    else:
                        print(f"   ❌ Nieprawidłowy JWT format")
                except Exception as e:
                    print(f"   ❌ Błąd dekodowania JWT: {e}")
        else:
            print(f"\n❌ Błąd {response.status_code}:")
            print(response.text)
            
    except Exception as e:
        print(f"\n❌ Exception: {e}")

def test_production_legacy_format():
    """Test legacy format dla porównania"""
    print("\n2️⃣ Test legacy format dla porównania:")
    
    base_url = "https://dtopsky.topsky.app"
    
    try:
        response = requests.post(
            f"{base_url}/acars/api/login/",
            json={
                "email": "laszewskimariusz@gmail.com",
                "api_key": "nowe_haslo123"
            },
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📄 Legacy format response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    print("🚀 Test szczegółowy produkcji SmartCARS")
    print("=" * 70)
    test_production_acars_login()
    test_production_legacy_format()
    print("=" * 70)
    print("📝 Jeśli session token jest generowany, problem może być w JWT payload") 