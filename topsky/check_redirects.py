#!/usr/bin/env python3
"""
Sprawdzenie przekierowań HTTP dla smartCARS
"""

import requests

def check_url_redirects(url):
    """Sprawdza przekierowania dla podanego URL"""
    print(f"🔍 Sprawdzam: {url}")
    
    try:
        # Wyłącz automatyczne przekierowania
        response = requests.get(url, allow_redirects=False, timeout=10)
        
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        if response.status_code in [301, 302, 307, 308]:
            location = response.headers.get('Location', 'BRAK')
            print(f"   🚨 PRZEKIEROWANIE DO: {location}")
            return location
        elif response.status_code == 200:
            print(f"   ✅ OK - brak przekierowania")
            return None
        else:
            print(f"   ⚠️ Nieoczekiwany status")
            return None
            
    except Exception as e:
        print(f"   ❌ Błąd: {e}")
        return None

def main():
    print("🚀 Sprawdzanie przekierowań dla smartCARS")
    print("=" * 60)
    
    # Wszystkie możliwe kombinacje URL
    urls_to_check = [
        "http://dtopsky.topsky.app/acars/api/",
        "https://dtopsky.topsky.app/acars/api/",
        "http://dtopsky.topsky.app/acars/api",
        "https://dtopsky.topsky.app/acars/api",
        "http://www.dtopsky.topsky.app/acars/api/",
        "https://www.dtopsky.topsky.app/acars/api/",
    ]
    
    redirects_found = []
    
    for url in urls_to_check:
        location = check_url_redirects(url)
        if location:
            redirects_found.append((url, location))
        print()
    
    print("=" * 60)
    if redirects_found:
        print("🚨 ZNALEZIONE PRZEKIEROWANIA:")
        for original, redirect in redirects_found:
            print(f"   {original} → {redirect}")
        print(f"\n💡 smartCARS NIE OBSŁUGUJE przekierowań!")
        print(f"   Użyj bezpośredniego URL bez przekierowań.")
    else:
        print("✅ Brak problematycznych przekierowań")

if __name__ == "__main__":
    main() 