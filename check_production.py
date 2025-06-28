import requests

try:
    response = requests.get('https://dtopsky.topsky.app/api/smartcars/', timeout=10)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Handler: {data.get('handler', {}).get('name')}")
        print(f"Version: {data.get('handler', {}).get('version')}")
        print("✅ Official smartCARS 3 API is working!")
    else:
        print(f"Error: {response.text[:200]}")
except Exception as e:
    print(f"Exception: {e}") 