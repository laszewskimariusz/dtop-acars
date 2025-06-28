import requests

def check_url_redirects():
    print("🔍 Sprawdzanie przekierowań URL...")
    
    urls_to_test = [
        "https://dtopsky.topsky.app/api/smartcars",      # Bez slash
        "https://dtopsky.topsky.app/api/smartcars/",     # Z slash
        "https://dtopsky.topsky.app/api/smartcars/login", # Login bez slash
        "https://dtopsky.topsky.app/api/smartcars/login/" # Login z slash
    ]
    
    for url in urls_to_test:
        try:
            # Użyj allow_redirects=False żeby zobaczyć rzeczywisty status
            response = requests.get(url, allow_redirects=False, timeout=10)
            print(f"📍 {url}")
            print(f"   Status: {response.status_code}")
            if 'location' in response.headers:
                print(f"   Redirect to: {response.headers['location']}")
            if response.status_code == 200:
                print("   ✅ OK - No redirect")
            elif response.status_code == 301:
                print("   ⚠️  301 Permanent Redirect (smartCARS problem!)")
            elif response.status_code == 302:
                print("   ⚠️  302 Temporary Redirect (smartCARS problem!)")
            print()
        except Exception as e:
            print(f"❌ {url} - Error: {e}")
            print()

if __name__ == "__main__":
    check_url_redirects() 