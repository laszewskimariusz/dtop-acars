import requests
import json

try:
    response = requests.get('https://dtopsky.topsky.app/api/smartcars/')
    print("Current API Response:")
    print("Status:", response.status_code)
    print("JSON:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Error: {e}") 