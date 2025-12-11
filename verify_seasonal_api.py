import requests
import json

api_url = 'http://localhost:58510/aggregates/seasonal-distribution'

try:
    print(f"Connecting to {api_url} (Timeout 30s)...")
    resp = requests.get(api_url, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print("Data Sample:", json.dumps(data[:3], indent=2))
        if isinstance(data, list) and len(data) > 0 and 'x' in data[0]:
            print("Format VALID.")
        else:
            print("Format INVALID.")
    else:
        print("Response Text:", resp.text)
except Exception as e:
    print(f"Error: {e}")
