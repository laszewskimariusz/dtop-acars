#!/usr/bin/env python3
"""
Test SmartCARS 3 na produkcji - dtopsky.topsky.app
"""

import requests
import json
import base64
from datetime import datetime

def decode_jwt_payload(token):
    """Decode JWT payload for inspection"""
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        payload_b64 = parts[1]
        padding = '=' * (4 - len(payload_b64) % 4)
        payload = base64.b64decode(payload_b64 + padding)
        return json.loads(payload.decode('utf-8'))
    except:
        return None

def test_production_smartcars():
    """Test complete SmartCARS 3 authentication flow on production"""
    print("🚀 SmartCARS 3 Production Test - dtopsky.topsky.app")
    print("=" * 60)
    
    base_url = "https://dtopsky.topsky.app"
    username = "laszewskimariusz@gmail.com"
    password = "nowe_haslo123"
    
    # Test 1: API Handler
    print("\n1️⃣ API Handler Test (Production)")
    print("-" * 40)
    
    try:
        api_response = requests.get(f"{base_url}/acars/api/", timeout=10)
        print(f"Status: {api_response.status_code}")
        
        if api_response.status_code == 200:
            data = api_response.json()
            print(f"✅ API Version: {data.get('apiVersion')}")
            print(f"✅ Handler: {data.get('handler', {}).get('name')}")
            print(f"✅ Status: {data.get('status')}")
            
            # Check if this is the new version
            handler_name = data.get('handler', {}).get('name', '')
            if 'Django ACARS Handler' in handler_name:
                print("✅ New SmartCARS 3 implementation detected!")
            else:
                print("⚠️  Old implementation detected - may need to redeploy")
                
        else:
            print(f"❌ API Handler failed: {api_response.status_code}")
            print(api_response.text)
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: SmartCARS 3 Login
    print("\n2️⃣ SmartCARS 3 Login Test (Production)")
    print("-" * 40)
    
    login_url = f"{base_url}/acars/api/login?username={username}"
    
    try:
        login_response = requests.post(
            login_url,
            json={"password": password},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print(f"❌ Login failed: {login_response.text}")
            return False
        
        login_data = login_response.json()
        
        # Verify SmartCARS 3 format
        required_fields = ['pilotID', 'session', 'expiry', 'firstName', 'lastName', 'email']
        missing_fields = [field for field in required_fields if field not in login_data]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            print(f"Response: {json.dumps(login_data, indent=2)}")
            return False
        
        print(f"✅ Pilot ID: {login_data['pilotID']}")
        print(f"✅ Email: {login_data['email']}")
        print(f"✅ Name: {login_data['firstName']} {login_data['lastName']}")
        
        session_token = login_data['session']
        expiry = login_data['expiry']
        
        # Verify JWT
        payload = decode_jwt_payload(session_token)
        if payload:
            print(f"✅ JWT Token valid")
            print(f"   - User ID: {payload.get('user_id')}")
            print(f"   - Token Type: {payload.get('token_type')}")
            exp_date = datetime.fromtimestamp(payload.get('exp', 0))
            print(f"   - Expires: {exp_date}")
        else:
            print("❌ JWT Token invalid")
            return False
            
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Test 3: User Info Endpoint
    print("\n3️⃣ User Info Test (Production)")
    print("-" * 40)
    
    try:
        user_response = requests.get(
            f"{base_url}/acars/api/user",
            headers={'Authorization': f'Bearer {session_token}'},
            timeout=10
        )
        
        print(f"Status: {user_response.status_code}")
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            print(f"✅ User Info Retrieved")
            print(f"   - Pilot ID: {user_data.get('pilotID')}")
            print(f"   - Email: {user_data.get('email')}")
            print(f"   - Total Flights: {user_data.get('total_flights')}")
            print(f"   - Status: {user_data.get('status')}")
        else:
            print(f"❌ User info failed: {user_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User info request failed: {e}")
        return False
    
    # Test 4: Authentication Persistence
    print("\n4️⃣ Authentication Persistence Test (Production)")
    print("-" * 40)
    
    try:
        ping_response = requests.get(
            f"{base_url}/acars/api/ping/",
            headers={'Authorization': f'Bearer {session_token}'},
            timeout=10
        )
        
        print(f"Ping Status: {ping_response.status_code}")
        
        if ping_response.status_code == 200:
            ping_data = ping_response.json()
            print(f"✅ Authentication persistent")
            print(f"   - Status: {ping_data.get('status')}")
            print(f"   - User: {ping_data.get('user')}")
        else:
            print(f"❌ Authentication not persistent: {ping_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ping request failed: {e}")
        return False
    
    # Test 5: SmartCARS Format Verification
    print("\n5️⃣ SmartCARS Format Verification (Production)")
    print("-" * 40)
    
    format_checks = [
        ("pilotID format", login_data['pilotID'].startswith('LO') and len(login_data['pilotID']) == 6),
        ("session is JWT", len(session_token.split('.')) == 3),
        ("expiry is timestamp", isinstance(expiry, int) and expiry > 1000000000),
        ("firstName present", bool(login_data['firstName'])),
        ("email format", '@' in login_data['email'])
    ]
    
    all_passed = True
    for check_name, passed in format_checks:
        status = "✅" if passed else "❌"
        print(f"   {status} {check_name}")
        if not passed:
            all_passed = False
    
    if not all_passed:
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("📊 Production SmartCARS 3 Compatibility Summary")
    print("=" * 60)
    
    compatibility_features = [
        ("✅ API Handler", "Production responds to smartCARS requests"),
        ("✅ Login Format", "Username in GET, password in POST works"),
        ("✅ Response Format", "Matches SmartCARS 3 specification"),
        ("✅ JWT Tokens", "Production authentication tokens work"),
        ("✅ User Endpoint", "Returns pilot information from production"),
        ("✅ Persistence", "Authentication works across production requests"),
        ("✅ Format Validation", "All production fields match expected format")
    ]
    
    for feature, description in compatibility_features:
        print(f"{feature}: {description}")
    
    print("\n🎉 Production SmartCARS 3 TFDI Compatibility: COMPLETE!")
    print("   Production API is ready for SmartCARS 3 usage!")
    
    print(f"\n📋 SmartCARS 3 Configuration:")
    print(f"   - ACARS URL: {base_url}/acars/api/")
    print(f"   - Login: Email + Password")
    print(f"   - Status: Ready for TFDI SmartCARS 3")
    
    return True

def test_debug_endpoints():
    """Test debug endpoints on production"""
    print("\n🔍 Debug Endpoints Test (Production)")
    print("-" * 40)
    
    base_url = "https://dtopsky.topsky.app"
    
    try:
        debug_response = requests.get(f"{base_url}/acars/api/debug/", timeout=10)
        print(f"Debug Status: {debug_response.status_code}")
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json()
            print(f"✅ Debug endpoint accessible")
            print(f"   - Total requests logged: {debug_data.get('total_requests', 0)}")
            
            recent = debug_data.get('recent_requests', [])
            if recent:
                print(f"   - Latest request: {recent[-1].get('timestamp')}")
                print(f"   - Latest path: {recent[-1].get('path')}")
        else:
            print(f"⚠️  Debug endpoint: {debug_response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Debug endpoint error: {e}")

if __name__ == "__main__":
    success = test_production_smartcars()
    test_debug_endpoints()
    
    if success:
        print("\n🚀 Production is ready for SmartCARS 3!")
        print("You can now configure TFDI SmartCARS 3 with:")
        print("URL: https://dtopsky.topsky.app/acars/api/")
    else:
        print("\n⚠️  Production issues detected - may need to redeploy changes.") 