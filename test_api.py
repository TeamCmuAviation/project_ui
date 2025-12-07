import requests
import json

api_base = 'http://localhost:58510'

try:
    print(f"Querying {api_base}/classification-results with evaluator_id='RONNIE'...")
    # Requesting limit 50
    resp = requests.get(f"{api_base}/classification-results", params={'skip': 0, 'limit': 50, 'evaluator_id': 'RONNIE'}, timeout=60)
    
    print(f"Status Code: {resp.status_code}")
    try:
        data = resp.json()
        with open('api_response.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        count = len(data) if isinstance(data, list) else 0
        print(f"Items returned: {count}")
        
        if count == 0:
            print("No items returned.")
        elif count > 50:
            print("WARNING: API returned more items than limit!")
        else:
            print("API returned respectable number of items (<= limit). Filtering might be working.")
            
        # Check if returned items are assigned to RONNIE (if that field is present)
        # Note: Spec doesn't guarantee 'evaluator_id' in response object, but checking just in case
        if count > 0 and isinstance(data[0], dict):
             if 'evaluator_id' in data[0]:
                 not_ronnie = [t for t in data if t.get('evaluator_id') != 'RONNIE']
                 if not_ronnie:
                     print(f"WARNING: Found {len(not_ronnie)} tasks NOT assigned to RONNIE.")
                 else:
                     print("All tasks appear to be assigned to RONNIE (based on response field).")
             else:
                 print("Response objects do not contain 'evaluator_id' field. Cannot verify assignment from response body.")

    except Exception as e:
        print(f"Failed to parse JSON: {e}")
        print(f"Raw text: {resp.text[:500]}")

except Exception as e:
    print(f"Request failed: {e}")
