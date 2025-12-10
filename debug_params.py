import requests
import json

API_BASE = "http://localhost:58510"

def check(name, params):
    print(f"\n--- {name} ---")
    print(f"Params: {params}")
    try:
        resp = requests.get(f"{API_BASE}/aggregates/top-n", params=params, timeout=5)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Count: {len(data) if isinstance(data, list) else 'Not a list'}")
        if isinstance(data, list) and len(data) > 0:
            print(f"First Item: {data[0]}")
        else:
            print("Response is empty.")
    except Exception as e:
        print(f"Error: {e}")

# 1. As done in views.py (with period)
check("With Period", {'category': 'final_category', 'n': 10, 'period': 'month'})

# 2. As done in Postman (without period)
check("Without Period", {'category': 'final_category', 'n': 10})
