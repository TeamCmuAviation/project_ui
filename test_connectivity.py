import requests
import json

api_base = 'http://localhost:58510'

try:
    print(f"Testing connectivity to {api_base}/airports...")
    # Try a simple GET request to a known fast endpoint
    resp = requests.get(f"{api_base}/airports", params={'codes': 'KJFK'}, timeout=5)
    
    print(f"Status Code: {resp.status_code}")
    try:
        data = resp.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Raw text: {resp.text[:200]}")

except Exception as e:
    print(f"Connectivity check failed: {e}")
