#!/usr/bin/env python3
"""
Real-time network logger for Django requests
"""
import requests
import time
import json
from datetime import datetime
import threading
import socket

def log_with_time(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {message}")

def test_django_api():
    """Test our Django API endpoints"""
    log_with_time("🧪 Testing our API endpoints...")
    
    # Our API endpoints
    api_base = "https://dtopsky.topsky.app/api/smartcars"
    
    # Test endpoints to verify they work
    test_endpoints = [
        f"{api_base}/",
        f"{api_base}/login"
    ]
    
    for endpoint in test_endpoints:
        try:
            if "login" in endpoint:
                # Test POST request like SmartCARS would send
                test_data = {
                    "email": "laszewskimariusz@gmail.com",
                    "password": "Syjon666"
                }
                
                log_with_time(f"📤 Testing POST {endpoint}")
                log_with_time(f"   Data: {test_data}")
                
                response = requests.post(
                    endpoint,
                    json=test_data,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': 'SmartCARS/3.0',
                        'Accept': 'application/json'
                    },
                    timeout=10
                )
                
                log_with_time(f"📥 Response: {response.status_code}")
                log_with_time(f"   Headers: {dict(response.headers)}")
                
                try:
                    response_data = response.json()
                    log_with_time(f"   Body: {json.dumps(response_data, indent=2)}")
                except:
                    log_with_time(f"   Body: {response.text}")
                    
            else:
                # Test GET request
                log_with_time(f"📤 Testing GET {endpoint}")
                
                response = requests.get(
                    endpoint,
                    headers={
                        'User-Agent': 'SmartCARS/3.0',
                        'Accept': 'application/json'
                    },
                    timeout=10
                )
                
                log_with_time(f"📥 Response: {response.status_code}")
                
                try:
                    response_data = response.json()
                    log_with_time(f"   Body: {json.dumps(response_data, indent=2)}")
                except:
                    log_with_time(f"   Body: {response.text}")
            
            log_with_time("-" * 40)
            
        except Exception as e:
            log_with_time(f"❌ Error testing {endpoint}: {e}")
    
    # Now test Basic Auth format
    log_with_time("🔐 Testing Basic Auth format...")
    
    import base64
    credentials = base64.b64encode("laszewskimariusz@gmail.com:Syjon666".encode()).decode()
    
    try:
        response = requests.post(
            f"{api_base}/login",
            headers={
                'Authorization': f'Basic {credentials}',
                'Content-Type': 'application/json',
                'User-Agent': 'SmartCARS/3.0'
            },
            json={},  # Empty body with Basic Auth
            timeout=10
        )
        
        log_with_time(f"📥 Basic Auth Response: {response.status_code}")
        
        try:
            response_data = response.json()
            log_with_time(f"   Body: {json.dumps(response_data, indent=2)}")
        except:
            log_with_time(f"   Body: {response.text}")
            
    except Exception as e:
        log_with_time(f"❌ Basic Auth test failed: {e}")

def check_smartcars_activity():
    """Check if SmartCARS is making requests to our API"""
    api_base = "https://dtopsky.topsky.app/api/smartcars"
    
    try:
        # Quick ping to see if there's activity
        response = requests.head(f"{api_base}/", timeout=2)
        return True
    except:
        return False

def monitor_continuous():
    """Continuously monitor for SmartCARS activity"""
    log_with_time("🔍 Starting continuous monitoring...")
    log_with_time("💡 This will show when SmartCARS makes requests to your API")
    log_with_time("🚀 Now try logging into SmartCARS!")
    log_with_time("=" * 60)
    
    last_activity_check = time.time()
    activity_counter = 0
    
    try:
        while True:
            # Check every 2 seconds
            time.sleep(2)
            
            current_time = time.time()
            
            # Show heartbeat every 30 seconds
            if current_time - last_activity_check > 30:
                log_with_time("💓 Monitoring active - waiting for SmartCARS requests...")
                last_activity_check = current_time
                activity_counter += 1
                
                # Every 2 minutes, remind user
                if activity_counter % 4 == 0:
                    log_with_time("💡 Make sure to:")
                    log_with_time("   1. Open SmartCARS 3")
                    log_with_time("   2. Enter URL: https://dtopsky.topsky.app/api/smartcars/")
                    log_with_time("   3. Enter your credentials and click Login/Connect")
                    log_with_time("-" * 40)
            
    except KeyboardInterrupt:
        log_with_time("🛑 Monitoring stopped by user")

def monitor_django_requests():
    """Main monitoring function"""
    log_with_time("🌐 Starting Django API Request Monitor")
    log_with_time("=" * 60)
    
    # First, test our API
    test_django_api()
    
    log_with_time("=" * 60)
    log_with_time("✅ API testing completed!")
    log_with_time("")
    
    # Then start continuous monitoring
    monitor_continuous()

if __name__ == "__main__":
    monitor_django_requests() 