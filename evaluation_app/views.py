from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import requests

# Hardcoded ICAO Taxonomies for the dropdown
ICAO_CATEGORIES = {
  "ADRM": {"name": "Aerodrome", "code": "ADRM", "description": " • Includes deficiencies/issues associated with State-approved Aerodrome runways, taxiways, ramp area..."},
  "AMAN": {"name": "Abrupt maneuvre", "code": "AMAN", "description": " • This category includes the intentional maneuvering of the aircraft to avoid a collision..."},
  "ARC": {"name": "Abnormal runway contact", "code": "ARC", "description": " • Any landing or takeoff involving abnormal runway or landing surface contact..."},
  "BIRD": {"name": "Birdstrike", "code": "BIRD", "description": " • A collision / near collision with or ingestion of one or several birds..."},
  "CABIN": {"name": "Cabin safety events", "code": "CABIN", "description": " • Includes occurrences related to cabin crew safety, security events..."},
  "GCOL": {"name": "Ground Collision", "code": "GCOL", "description": " • Includes collisions with an aircraft, person, ground vehicle, obstacle, building, structure, etc. while on a surface other than the runway..."},
  "LOC-G": {"name": "Loss of control - ground", "code": "LOC-G", "description": " • Loss of aircraft control while the aircraft is on the ground..."},
  "LOC-I": {"name": "Loss of control - inflight", "code": "LOC-I", "description": " • Loss of aircraft control while the aircraft is in flight..."},
  "LOLI": {"name": "Loss of lifting conditions en-route", "code": "LOLI", "description": " • Applicable only to aircraft that rely on static lift to maintain or increase flight altitude..."},
  "RAMP": {"name": "Ground Handling", "code": "RAMP", "description": " • Failures or malfunctions of the onboard external load handling lifting equipment or release systems..."},
  "RE": {"name": "Runway excursion", "code": "RE", "description": " • Only applicable during either the takeoff or landing phase..."},
  "TURB": {"name": "Turbulence encounter", "code": "TURB", "description": " • Uncontrolled movement or violent contact due to rough air..."},
  "UIMC": {"name": "Unintended flight in IMC", "code": "UIMC", "description": " • Applicable if the pilot was flying according to Visual Flight Rules (VFR) but inadvertently entered Instrument Meteorological Conditions..."},
  "WSTRW": {"name": "Windshear or thunderstorm", "code": "WSTRW", "description": " • Occurrences involving severe weather phenomena..."},
  "OTHR": {"name": "Other", "code": "OTHR", "description": " • This category includes any occurrence type that is not covered by any other category."},
  "UNK": {"name": "Unknown or undetermined", "code": "UNK", "description": " • Includes cases where the aircraft is missing..."},
  "ATM": {"name": "Air traffic management", "code": "ATM", "description": " • Occurrences involving Air traffic management or communications, navigation, or surveillance service issues"},
  "CFIT": {"name": "CFIT", "code": "CFIT", "description": " • Inflight collision or near collision with terrain, water, or obstacle without indication of loss of control"},
  "FUEL": {"name": "Fuel related", "code": "FUEL", "description": " • Powerplant issues due to fuel exhaustion, starvation, contamination or wrong fuel"},
  "ICE": {"name": "Icing", "code": "ICE", "description": " • Accumulation of snow, ice, freezing rain, or frost on aircraft surfaces"},
  "MAC": {"name": "MAC", "code": "MAC", "description": " • Airprox, ACAS alerts, loss of separation, near collisions between aircraft"},
  "RI": {"name": "Runway incursion", "code": "RI", "description": " • Runway incursion - vehicle, aircraft or person"},
  "SCF-NP": {"name": "System Failure (Non-Powerplant)", "code": "SCF-NP", "description": " • Failure or malfunction of an aircraft system or component - other than powerplant"},
  "SCF-PP": {"name": "System Failure (Powerplant)", "code": "SCF-PP", "description": " • Failure or malfunction of an aircraft system or component - related to powerplant"}
}

VALID_EVALUATORS = ['BARAKA', 'RONNIE', 'NASIRU', 'JB']

class LoginView(View):
    def get(self, request):
        return render(request, 'evaluation_app/login.html')

    def post(self, request):
        code = request.POST.get('access_code', '').strip().upper()
        if code in VALID_EVALUATORS:
            request.session['evaluator_id'] = code
            return redirect('task_list')
        else:
            messages.error(request, "Invalid access code. Access denied.")
            return redirect('login')


class TaskListView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('evaluator_id'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
        tasks = []
        
        # Pagination Parameters
        try:
            page = int(request.GET.get('page', 1))
            if page < 1: page = 1
        except ValueError:
            page = 1
            
        limit = 50
        skip = (page - 1) * limit

        try:
            # Pass skip and limit to the API
            resp = requests.get(f"{api_base}/classification-results", params={'skip': skip, 'limit': limit}, timeout=120)
            if resp.status_code == 200:
                all_tasks = resp.json()
                # Filter out completed tasks
                tasks = [t for t in all_tasks if not t.get('is_complete')]
            else:
                messages.error(request, f"Failed to fetch tasks: {resp.text}")
        except requests.RequestException as e:
            messages.error(request, f"Error connecting to API: {e}")
        
        # Simple pagination logic: if we got full limit, assume there's a next page
        has_next = len(all_tasks) == limit if 'all_tasks' in locals() else False
        has_prev = page > 1
        
        context = {
            'tasks': tasks,
            'evaluator_id': request.session['evaluator_id'],
            'page': page,
            'has_next': has_next,
            'has_prev': has_prev
        }
        return render(request, 'evaluation_app/task_list.html', context)


class EvaluationInterfaceView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('evaluator_id'):
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, uid):
        api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
        
        try:
            # Use bulk endpoint to fetch single item because detail endpoint is missing
            payload = [uid]
            data_resp = requests.post(f"{api_base}/full_classification_results_bulk", json=payload, timeout=120)
            
            if data_resp.status_code != 200:
                messages.error(request, f"Could not load data for UID {uid}")
                return redirect('task_list')
            
            resp_json = data_resp.json()
            full_data = resp_json.get('results', {}).get(uid)
            
            if not full_data:
                 messages.error(request, f"No data found for UID {uid}")
                 return redirect('task_list')

            # API returns flattened fields for origin (e.g. origin_narrative)
            # We reconstruct the 'origin' dict so the template works without changes
            origin_data = {
                'narrative': full_data.get('origin_narrative'),
                'date': full_data.get('origin_date'),
                'phase': full_data.get('origin_phase'),
                'aircraft_type': full_data.get('origin_aircraft_type'),
                'location': full_data.get('origin_location'),
                'operator': full_data.get('origin_operator'),
                # Add title/description if they map to something, or generic fallback
                'description': full_data.get('origin_narrative')[:200] + "..." if full_data.get('origin_narrative') else ""
            }
            
            classification_data = full_data 
            
        except requests.RequestException as e:
             messages.error(request, f"Error fetching case details: {e}")
             return redirect('task_list')
        
        context = {
            'origin': origin_data,
            'classification': classification_data,
            'categories': ICAO_CATEGORIES,
            'uid': uid,
            'classification_result_id': full_data.get('id')
        }
        return render(request, 'evaluation_app/evaluation_interface.html', context)

    def post(self, request, uid):
        evaluator_id = request.session['evaluator_id']
        api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
        
        # We need classification_result_id. It should be in the hidden field or inferred.
        # Let's expect it in POST
        classification_result_id = request.POST.get('classification_result_id')
        
        payload = {
            "classification_result_id": classification_result_id,
            "evaluator_id": evaluator_id,
            "human_category": request.POST.get('human_category'),
            "human_confidence": float(request.POST.get('human_confidence')),
            "human_reasoning": request.POST.get('human_reasoning')
        }

        try:
            submit_resp = requests.post(f"{api_base}/human_evaluation/submit", json=payload, timeout=120)
            if submit_resp.status_code == 200:
                messages.success(request, f"Evaluation for {uid} Submitted!")
            else:
                messages.error(request, f"Submission failed: {submit_resp.text}")
        except requests.RequestException as e:
            messages.error(request, f"Submission error: {e}")

        return redirect('task_list')
