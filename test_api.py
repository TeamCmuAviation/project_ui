import requests
import json

api_base = 'http://localhost:58510'

try:
    print(f"Querying {api_base}/classification-results with evaluator_id='RONNIE' (Upper)...")
    resp_upper = requests.get(f"{api_base}/classification-results", params={'skip': 0, 'limit': 10, 'evaluator_id': 'RONNIE'}, timeout=10)
    print(f"Upper Status: {resp_upper.status_code}, Items: {len(resp_upper.json()) if resp_upper.status_code == 200 else 'Err'}")

    print(f"Querying {api_base}/classification-results with evaluator_id='ronnie' (Lower)...")
    resp_lower = requests.get(f"{api_base}/classification-results", params={'skip': 0, 'limit': 10, 'evaluator_id': 'ronnie'}, timeout=10)
    print(f"Lower Status: {resp_lower.status_code}, Items: {len(resp_lower.json()) if resp_lower.status_code == 200 else 'Err'}")


except Exception as e:
    print(f"Request failed: {e}")
