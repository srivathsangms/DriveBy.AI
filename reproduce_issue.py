
import requests

import time
url = "http://localhost:8000/auth/register"
email = f"test_repro_{int(time.time())}@example.com"
payload = {
    "email": email,
    "password": "password123",
    "name": "Test User",
    "role": "driver"
}

try:
    response = requests.post(url, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
