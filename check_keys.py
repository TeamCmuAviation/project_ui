import requests
import json

try:
    resp = requests.get('http://localhost:58510/classification-results?limit=1', timeout=30)
    with open('keys.txt', 'w') as f:
        if resp.status_code == 200:
            data = resp.json()
            if data and isinstance(data, list):
                f.write(json.dumps(list(data[0].keys())))
                f.write("\n")
                f.write(json.dumps(data[0]))
            else:
                f.write("Response is not a list or empty")
        else:
            f.write(f"Error: {resp.status_code}")
except Exception as e:
    with open('keys.txt', 'w') as f:
        f.write(str(e))
