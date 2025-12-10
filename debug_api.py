import requests
import json
import os

API_BASE = "http://localhost:58510"

def check_endpoint(name, url, params=None):
    print(f"\n--- Checking {name} with params={params} ---")
    try:
        resp = requests.get(url, params=params, timeout=5)
        print(f"Status: {resp.status_code}")
        try:
            data = resp.json()
            print(f"Data Sample: {json.dumps(data, indent=2)[:500]}...")
        except:
            print(f"Raw Text: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

# Check Statistics with empty params
check_endpoint("Statistics (Empty Params)", f"{API_BASE}/aggregates/statistics", {})
