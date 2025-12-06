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
        try:
            resp = requests.get(f"{api_base}/classification-results", timeout=5)
            if resp.status_code == 200:
                tasks = resp.json()
            else:
                messages.error(request, f"Failed to fetch tasks: {resp.text}")
        except requests.RequestException as e:
            messages.error(request, f"Error connecting to API: {e}")
        
        context = {
            'tasks': tasks,
            'evaluator_id': request.session['evaluator_id']
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
            data_resp = requests.get(f"{api_base}/full_classification_results/{uid}", timeout=5)
            if data_resp.status_code != 200:
                messages.error(request, f"Could not load data for UID {uid}")
                return redirect('task_list')
            
            full_data = data_resp.json()
            # The structure from prompt: "combined JSON payload with classification... and origin"
            # Let's assume the top level keys are 'origin' and 'classification' or mixed.
            # Based on earlier code it seemed to be 'origin' key.
            # Let's assume the API returns the merged dict or specific keys.
            # Ideally we pass 'full_data' to template and let template handle it, 
            # but we need 'origin' specifically for display if separated.
            
            # Re-reading prompt: "Returns a combined JSON payload with classification (...) and origin (normalized report details)."
            # So likely: { "id":..., "origin": { ... }, ... }
            
            origin_data = full_data.get('origin', {})
            classification_data = full_data # The whole object acts as classification data wrapper
            
        except requests.RequestException:
             messages.error(request, "Error fetching case details.")
             return redirect('task_list')
        
        context = {
            'origin': origin_data,
            'classification': classification_data,
            'categories': ICAO_CATEGORIES,
            'uid': uid
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
            submit_resp = requests.post(f"{api_base}/human_evaluation/submit", json=payload, timeout=5)
            if submit_resp.status_code == 200:
                messages.success(request, f"Evaluation for {uid} Submitted!")
            else:
                messages.error(request, f"Submission failed: {submit_resp.text}")
        except requests.RequestException as e:
            messages.error(request, f"Submission error: {e}")

        return redirect('task_list')
