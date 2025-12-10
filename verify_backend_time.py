import requests
import json

URL = "http://localhost:8000/dashboard/api/category-data/"
params = {
    'start_period': '2000-01',
    'end_period': '2000-12'
}

try:
    print(f"Requesting {URL} with params {params}...")
    resp = requests.get(URL, params=params, timeout=10)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Data type: {type(data)}")
        print(f"Length: {len(data)}")
        if len(data) > 0:
            print(f"First item: {data[0]}")
            # check for 'OTHER' and count ~967 if user metadata is reliable, 
            # but user said 'endpoint URL ... yields ...' so we expect that data.
            # User sample data: {"category_value": "OTHER", "incident_count": 967}
            found = False
            for item in data:
                if item.get('category_value') == 'OTHER':
                    print(f"Found OTHER: {item}")
                    found = True
                    break
            if not found:
                print("OTHER category not found in top 10")
    else:
        print(f"Error: {resp.text}")
except Exception as e:
    print(f"Exception: {e}")
