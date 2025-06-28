import requests
import json

BASE_URL = "https://dtopsky.topsky.app/api/smartcars"
CREDENTIALS = {
    "email": "laszewskimariusz@gmail.com",
    "api_key": "nowe_haslo123"
}

def test_production_api():
    print("🚀 Test oficjalnego smartCARS 3 API na produkcji")
    print("=" * 60)
    
    # Test 1: Handler
    print("🧪 Test Handler...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Handler: {data.get('handler', {}).get('name')}")
            print(f"✅ Version: {data.get('handler', {}).get('version')}")
        else:
            print(f"❌ Handler failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Handler error: {e}")
    
    # Test 2: Login
    print("\n🧪 Test Login...")
    session_token = None
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json=CREDENTIALS,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            session_token = data.get('session')
            print(f"✅ Login successful! Pilot ID: {data.get('pilot_id')}")
            print(f"✅ Name: {data.get('name')}")
            print(f"✅ Session token received")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test 3: User Info
    if session_token:
        print("\n🧪 Test User Info...")
        try:
            response = requests.get(
                f"{BASE_URL}/user?session={session_token}",
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User info: Pilot {data.get('pilot_id')}")
                print(f"✅ Total flights: {data.get('total_flights')}")
            else:
                print(f"❌ User info failed: {response.status_code}")
        except Exception as e:
            print(f"❌ User info error: {e}")
    
    # Test 4: Data endpoints
    if session_token:
        print("\n🧪 Test Data Endpoints...")
        for endpoint in ['schedules', 'aircraft', 'airports']:
            try:
                response = requests.get(
                    f"{BASE_URL}/{endpoint}?session={session_token}",
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ {endpoint}: {len(data)} records")
                else:
                    print(f"❌ {endpoint} failed: {response.status_code}")
            except Exception as e:
                print(f"❌ {endpoint} error: {e}")
    
    print("\n=" * 60)
    if session_token:
        print("🎉 GOTOWE! smartCARS 3 API działa na produkcji!")
        print()
        print("📱 Konfiguracja dla smartCARS 3:")
        print(f"Script URL: {BASE_URL}")
        print(f"Email: {CREDENTIALS['email']}")
        print(f"API Key: {CREDENTIALS['api_key']}")
        print()
        print("✈️ Możesz teraz skonfigurować smartCARS 3!")
    else:
        print("❌ Problem z logowaniem - sprawdź dane")

if __name__ == "__main__":
    test_production_api() 