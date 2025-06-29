#!/usr/bin/env python3
"""
Monitor SmartCARS local API for real-time logging
"""
import requests
import time
import json
from datetime import datetime
import threading
import socket

class SmartCARSMonitor:
    def __init__(self):
        self.base_url = "http://localhost:7172"
        self.running = False
        self.endpoints = [
            "/api/identity", 
            "/api/status",
            "/api/plugins",
            "/api/settings",
            "/",
            "/status"
        ]
    
    def log(self, message):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] {message}")
    
    def check_smartcars_running(self):
        """Check if SmartCARS is running on port 7172"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', 7172))
            sock.close()
            return result == 0
        except:
            return False
    
    def test_endpoint(self, endpoint):
        """Test a specific endpoint"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, timeout=2)
            
            self.log(f"✅ {endpoint} -> {response.status_code}")
            
            # Try to parse JSON
            try:
                data = response.json()
                if len(str(data)) < 500:  # Only show short responses
                    self.log(f"   Data: {json.dumps(data, indent=2)}")
                else:
                    self.log(f"   Data: Large response ({len(str(data))} chars)")
            except:
                content = response.text[:200]
                self.log(f"   Content: {content}...")
                
        except requests.exceptions.ConnectionError:
            self.log(f"❌ {endpoint} -> Connection refused")
        except requests.exceptions.Timeout:
            self.log(f"⏱️  {endpoint} -> Timeout")
        except Exception as e:
            self.log(f"❌ {endpoint} -> Error: {e}")
    
    def monitor_endpoints(self):
        """Monitor all endpoints periodically"""
        self.log("🔍 Starting endpoint monitoring...")
        
        while self.running:
            if not self.check_smartcars_running():
                self.log("❌ SmartCARS not running on port 7172")
                time.sleep(5)
                continue
            
            self.log("📡 SmartCARS detected - checking endpoints...")
            
            for endpoint in self.endpoints:
                if not self.running:
                    break
                self.test_endpoint(endpoint)
                time.sleep(0.5)
            
            self.log("=" * 50)
            time.sleep(10)  # Check every 10 seconds
    
    def monitor_network_traffic(self):
        """Monitor network requests to our API"""
        self.log("🌐 Starting network traffic monitoring...")
        
        # This would require more complex packet sniffing
        # For now, we'll check our Django logs
        while self.running:
            time.sleep(5)
    
    def test_our_api(self):
        """Test our own API to verify it's working"""
        self.log("🧪 Testing our API...")
        
        our_endpoints = [
            "https://dtopsky.topsky.app/api/smartcars/",
            "https://dtopsky.topsky.app/api/smartcars/login"
        ]
        
        for endpoint in our_endpoints:
            try:
                if "login" in endpoint:
                    # Test login endpoint
                    response = requests.post(
                        endpoint,
                        json={"email": "test@topsky.app", "password": "testpassword123"},
                        timeout=5
                    )
                else:
                    # Test info endpoint
                    response = requests.get(endpoint, timeout=5)
                
                self.log(f"✅ Our API {endpoint} -> {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.log(f"   ✅ Valid JSON response")
                    except:
                        self.log(f"   ❌ Invalid JSON response")
                else:
                    self.log(f"   ❌ Error response: {response.text[:100]}")
                    
            except Exception as e:
                self.log(f"❌ Our API {endpoint} -> Error: {e}")
    
    def run_comprehensive_test(self):
        """Run a comprehensive test of SmartCARS integration"""
        self.log("🚀 Starting SmartCARS Monitor")
        self.log("=" * 60)
        
        # Test our API first
        self.test_our_api()
        self.log("-" * 40)
        
        # Check SmartCARS status
        if self.check_smartcars_running():
            self.log("✅ SmartCARS is running on port 7172")
            
            # Test all endpoints once
            for endpoint in self.endpoints:
                self.test_endpoint(endpoint)
                time.sleep(0.5)
        else:
            self.log("❌ SmartCARS is not running on port 7172")
            self.log("   Please start SmartCARS and try again")
            return
        
        self.log("=" * 60)
        self.log("🔍 Starting continuous monitoring (Ctrl+C to stop)...")
        
        # Start continuous monitoring
        self.running = True
        
        try:
            # Start monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_endpoints)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Keep main thread alive
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("\n🛑 Stopping monitor...")
            self.running = False

def main():
    monitor = SmartCARSMonitor()
    monitor.run_comprehensive_test()

if __name__ == "__main__":
    main() 