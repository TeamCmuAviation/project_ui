from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.conf import settings
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
import requests
import json

# Hardcoded ICAO Taxonomies for the dropdown
# Rich ICAO Taxonomies for the dropdown
ICAO_CATEGORIES = {
    "ADRM": {
      "name": "Aerodrome",
      "description": " • Includes deficiencies/issues associated with State-approved Aerodrome runways, taxiways, ramp area, parking area, buildings and structures, Crash/Fire/Rescue (CFR) services, obstacles on the Aerodrome property, lighting, markings, signage, procedures, policies, and standards. • Examples include closed runways, improperly marked runways, construction interference, lighting failures, signage limitations, etc. • Occurrences do not necessarily involve an aircraft. • Effects of Aerodrome design ar",
      "code": "ADRM",
      "examples": [
        "closed runways",
        "improperly marked runways",
        "construction interference"
      ],
      "number": "24"
    },
    "AMAN": {
      "name": "Abrupt maneuvre",
      "description": " • This category includes the intentional maneuvering of the aircraft to avoid a collision with terrain, objects/obstacles, weather or other aircraft (Note: The effect of intentional maneuvering is the key consideration). • Abrupt maneuvering may also result in a loss of control or system/component failure or malfunction. In this case, the event is coded under both categories (e.g., AMAN and Loss of Control–Inflight (LOC–I), AMAN and System/Component Failure or Malfunction (Non- Powerplant) (SCF",
      "code": "AMAN",
      "examples": [
        "the intentional maneuvering of the aircraft to avoid a collision with terrain",
        "objects/obstacles",
        "weather or other aircraft (Note: The effect of intentional maneuvering is the key consideration)."
      ],
      "number": "1"
    },
    "ARC": {
      "name": "Abnormal runway contact",
      "description": "ABNORMAL RUNWAY CONTACT (ARC) Any landing or takeoff involving abnormal runway or landing surface contact. • Events such as hard/heavy landings, long/fast landings, off center landings, crabbed landings, nose wheel first touchdown, tail strikes, and wingtip/nacelle strikes are included in this category. • Gear-up landings are also recorded here. However, if a system/component failure or malfunction occurred, which led to the gear up landing, the event is also coded under the appropriate system/c",
      "code": "ARC",
      "examples": [
        "hard/heavy landings",
        "long/fast landings",
        "off center landings"
      ],
      "number": "2"
    },
    "BIRD": {
      "name": "Birdstrike",
      "description": "A collision / near collision with or ingestion of one or several birds. • May occur in any phase of flight",
      "code": "BIRD",
      "examples": [],
      "number": "29"
    },
    "CABIN": {
      "name": "Cabin safety events",
      "description": "Includes occurrences related to cabin crew safety, security events...",
      "code": "CABIN",
      "examples": [],
      "number": "26"
    },
    "GCOL": {
      "name": "Ground Collision",
      "description": " • Includes collisions with an aircraft, person, ground vehicle, obstacle, building, structure, etc. while on a surface other than the runway used for landing or intended for takeoff. • Ground collisions resulting from events categorized under Runway Incursion (RI), Wildlife (WILD) or Ground Handling (RAMP) are excluded from this category.",
      "code": "GCOL",
      "examples": [
        "collisions with an aircraft",
        "ground vehicle"
      ],
      "number": "9"
    },
    "LOC-G": {
      "name": "Loss of control - ground",
      "description": "Loss of aircraft control while the aircraft is on the ground...",
      "code": "LOC-G",
      "examples": [],
      "number": "12"
    },
    "LOC-I": {
      "name": "Loss of control - inflight",
      "description": "• NOTE: excluding rotorcraft air taxi phase of flight. • NOTE: includes maneuvering at low height while searching for an off-aerodrome landing location. Do not use LALT in conjunction with CFIT. Loss of aircraft control while the aircraft is on the ground (LOC-G: Loss of control - ground)",
      "code": "LOC-I",
      "examples": [
        "maneuvering at low height while searching for an off-aerodrome landing location."
      ],
      "number": "13"
    },
    "LOLI": {
      "name": "Loss of lifting conditions en-route",
      "description": " • Applicable only to aircraft that rely on static lift to maintain or increase flight altitude, namely sailplanes, gliders, hang gliders and paragliders, balloons and airships. • All static lift forms to be considered, including atmospheric lift, namely from Orographic, Thermal, Mountain Wave and Convergence Zone, and buoyancy lift namely from lighter than air gas or hot air. • Also include motorglider and paramotor aircraft if operating under static atmospheric lift conditions and the engine c",
      "code": "LOLI",
      "examples": [],
      "number": "103"
    },
    "RAMP": {
      "name": "Ground Handling",
      "description": "• Failures or malfunctions of the onboard external load handling lifting equipment or release systems should be coded under SCF-NP, as these are considered to be aircraft systems. Fire or smoke in or on the aircraft, in flight or on the ground, which is not the result of impact. (F-NI: Fire/smoke 5 (non-impact)) • Includes fire due to a combustive explosion from an accidental ignition source. • Includes fire and smoke from system/component failures/malfunctions in the cockpit, passenger cabin, o",
      "code": "RAMP",
      "examples": [
        "fire due to a combustive explosion from an accidental ignition source."
      ],
      "number": "8"
    },
    "RE": {
      "name": "Runway excursion",
      "description": " • Only applicable during either the takeoff or landing phase • The excursion may be intentional or unintentional. For example, the deliberate veer off to avoid a collision, brought about by a Runway Incursion. In this case, code both categories • Use RE in all cases where the aircraft left the runway/helipad/helideck regardless of whether the excursion was the consequence of another event or not. Any occurrence at an aerodrome involving the incorrect presence of an aircraft, vehicle or person o",
      "code": "RE",
      "examples": [],
      "number": "15"
    },
    "TURB": {
      "name": "Turbulence encounter",
      "description": "appropriate. • Includes heliports (excludes unprepared or natural landing sites). • Includes loose foreign objects on aerodromes and on heliports (excludes unprepared or natural landing sites). Includes failure of winch launch equipment for gliders. The intentional abrupt maneuvering of the aircraft by the flight crew. (AMAN: Abrupt maneuvre) 1 • This category includes the intentional maneuvering of the aircraft to avoid a collision with terrain, objects/obstacles, weather or other aircraft (Not",
      "code": "TURB",
      "examples": [
        "heliports (excludes unprepared or natural landing sites).",
        "loose foreign objects on aerodromes and on heliports (excludes unprepared or natural landing sites).",
        "failure of winch launch equipment for gliders."
      ],
      "number": "21"
    },
    "UIMC": {
      "name": "Unintended flight in IMC",
      "description": " • May be used as a precursor to CFIT, LOC-I or LALT. • Applicable if the pilot was flying according to Visual Flight Rules (VFR), as defined in Annex 2 – Rules of the Air – to the Convention on International Civil Aviation and by any reason found oneself inadvertently in IMC • Only to be used when loss of visual references is encountered, • Only to be used if pilot not qualified to fly in IMC and/or aircraft not equipped to fly in IMC A touchdown off the runway surface. (USOS: Undershoot/oversh",
      "code": "UIMC",
      "examples": [],
      "number": "100"
    },
    "WSTRW": {
      "name": "Windshear or thunderstorm",
      "description": "appropriate. • Includes heliports (excludes unprepared or natural landing sites). • Includes loose foreign objects on aerodromes and on heliports (excludes unprepared or natural landing sites). Includes failure of winch launch equipment for gliders. The intentional abrupt maneuvering of the aircraft by the flight crew. (AMAN: Abrupt maneuvre) 1 • This category includes the intentional maneuvering of the aircraft to avoid a collision with terrain, objects/obstacles, weather or other aircraft (Not",
      "code": "WSTRW",
      "examples": [
        "heliports (excludes unprepared or natural landing sites).",
        "loose foreign objects on aerodromes and on heliports (excludes unprepared or natural landing sites).",
        "failure of winch launch equipment for gliders."
      ],
      "number": "23"
    },
    "OTHR": {
      "name": "Other",
      "description": "This category includes any occurrence type that is not covered by any other category.",
      "code": "OTHR",
      "examples": [
        "any occurrence type that is not covered by any other category."
      ],
      "number": "98"
    },
    "UNK": {
      "name": "Unknown or undetermined",
      "description": " • Includes cases where the aircraft is missing. • Includes those occurrences where there is not enough information at hand to classify the occurrence or where additional information is expected in due course to better classify the occurrence.",
      "code": "UNK",
      "examples": [
        "cases where the aircraft is missing.",
        "those occurrences where there is not enough information at hand to classify the occurrence or where additional information is expected in due course to better classify the occurrence."
      ],
      "number": "99"
    },
    "ATM": {
      "name": "Air traffic management",
      "description": "Occurrences involving Air traffic management or communications, navigation, or surveillance service issues",
      "code": "ATM",
      "examples": []
    },
    "CFIT": {
      "name": "CFIT",
      "description": "Inflight collision or near collision with terrain, water, or obstacle without indication of loss of control",
      "code": "CFIT",
      "examples": []
    },
    "FUEL": {
      "name": "Fuel related",
      "description": "Powerplant issues due to fuel exhaustion, starvation, contamination or wrong fuel",
      "code": "FUEL",
      "examples": []
    },
    "ICE": {
      "name": "Icing",
      "description": "Accumulation of snow, ice, freezing rain, or frost on aircraft surfaces",
      "code": "ICE",
      "examples": []
    },
    "MAC": {
      "name": "MAC",
      "description": "Airprox, ACAS alerts, loss of separation, near collisions between aircraft",
      "code": "MAC",
      "examples": []
    },
    "RI": {
      "name": "Runway incursion",
      "description": "Runway incursion - vehicle, aircraft or person",
      "code": "RI",
      "examples": []
    },
    "SCF-NP": {
      "name": "System Failure (Non-Powerplant)",
      "description": "Failure or malfunction of an aircraft system or component - other than powerplant",
      "code": "SCF-NP",
      "examples": []
    },
    "SCF-PP": {
      "name": "System Failure (Powerplant)",
      "description": "Failure or malfunction of an aircraft system or component - related to powerplant",
      "code": "SCF-PP",
      "examples": []
    }
}

VALID_EVALUATORS = ['BARAKA', 'RONNIE', 'NASIRU', 'JB']

class LoginView(View):
    def get(self, request):
        return render(request, 'evaluation_app/login.html')

    def post(self, request):
        code = request.POST.get('access_code', '').strip().upper()
        if code in VALID_EVALUATORS:
            request.session['evaluator_id'] = code
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('task_list')
        else:
            messages.error(request, "Invalid access code. Access denied.")
            return redirect('login')

def logout_view(request):
    request.session.flush()
    messages.success(request, "Logged out successfully.")
    return redirect('dashboard')


class TaskListView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('evaluator_id'):
            from django.urls import reverse
            return redirect(f"{reverse('login')}?next={request.path}")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
        evaluator_id = request.session['evaluator_id']
        
        # Initialize stats
        total_tasks = 0
        completed_tasks_count = 0
        pending_tasks = []
        progress_percentage = 0
        
        try:
            # Fetch ALL tasks for the evaluator to calculate progress
            # Using a high limit to ensure we get everything
            resp = requests.get(
                f"{api_base}/classification-results", 
                params={'skip': 0, 'limit': 5000, 'evaluator_id': evaluator_id}, 
                timeout=120
            )
            
            if resp.status_code == 200:
                all_tasks = resp.json()
                total_tasks = len(all_tasks)
                
                # Separation of concerns: Filter in Python
                completed_tasks = [t for t in all_tasks if t.get('is_complete')]
                pending_tasks = [t for t in all_tasks if not t.get('is_complete')]
                
                completed_tasks_count = len(completed_tasks)
                
                if total_tasks > 0:
                    progress_percentage = int((completed_tasks_count / total_tasks) * 100)
            else:
                messages.error(request, f"Failed to fetch tasks: {resp.text}")
                
        except requests.RequestException as e:
            messages.error(request, f"Error connecting to API: {e}")
        
        context = {
            'tasks': pending_tasks, # Only show pending tasks in the list
            'evaluator_id': evaluator_id,
            'total_tasks': total_tasks,
            'completed_tasks_count': completed_tasks_count,
            'progress_percentage': progress_percentage
        }
        return render(request, 'evaluation_app/task_list.html', context)

@login_required
def random_task(request):
    """
    Redirects to a random pending task for the current evaluator.
    """
    api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
    evaluator_id = request.session.get('evaluator_id')
    
    if not evaluator_id:
        return redirect('login')
        
    try:
        # Fetch pending tasks
        # We could potentially optimize this if the API supported filtering by status
        resp = requests.get(
            f"{api_base}/classification-results", 
            params={'skip': 0, 'limit': 5000, 'evaluator_id': evaluator_id}, 
            timeout=120
        )
        
        if resp.status_code == 200:
            all_tasks = resp.json()
            pending_tasks = [t for t in all_tasks if not t.get('is_complete')]
            
            if pending_tasks:
                import random
                # Pick a random task
                selected_task = random.choice(pending_tasks)
                # Redirect to the evaluation interface for this task
                return redirect('evaluate', uid=selected_task['source_uid'])
            else:
                messages.info(request, "🎉 You have completed all assigned tasks!")
                return redirect('task_list')
        else:
            messages.error(request, "Failed to fetch tasks for random selection.")
            return redirect('task_list')
            
    except requests.RequestException as e:
        messages.error(request, f"Error connecting to API: {e}")
        return redirect('task_list')


class EvaluationInterfaceView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('evaluator_id'):
            from django.urls import reverse
            return redirect(f"{reverse('login')}?next={request.path}")
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
            "classification_result_id": int(classification_result_id),
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


class DashboardView(View):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
        
        # Extract filters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        operator = request.GET.get('operator')
        phase = request.GET.get('phase')
        aircraft_type = request.GET.get('aircraft_type')

        # Build query params
        params = {}
        if start_date: params['start_date'] = start_date
        if end_date: params['end_date'] = end_date
        if operator: params['operator'] = operator
        if phase: params['phase'] = phase
        if aircraft_type: params['aircraft_type'] = aircraft_type

        # Fetch Data
        context = {
            'filters': {
                'start_date': start_date,
                'end_date': end_date,
                'operator': operator,
                'phase': phase,
                'aircraft_type': aircraft_type
            },
            'categories': ICAO_CATEGORIES  # Reuse existing categories for filters if needed
        }

        try:
            # 1. Key Metrics (Statistics)
            # GET /aggregates/statistics
            resp_stats = requests.get(f"{api_base}/aggregates/statistics", params=params, timeout=10)
            if resp_stats.status_code == 200:
                stats = resp_stats.json()
                # Assuming stats returns keys like 'total_incidents', 'fatal_incidents', 'fatalities', etc.
                # If structure is different, we fallback to defaults.
                context['metric_incidents'] = stats.get('total_incidents', 0)
                context['metric_fatal'] = stats.get('fatal_incidents', 0)
                context['metric_fatalities'] = stats.get('total_fatalities', 0)
                # Derived or extra metrics if available
                context['metric_ground'] = stats.get('ground_incidents', 0) 
                
                fatal = stats.get('fatal_incidents', 0)
                non_fatal = stats.get('total_incidents', 0) - fatal
                context['metric_split'] = f"{fatal} Fatal / {non_fatal} Non-Fatal"
            else:
                 # Fallbacks
                context['metric_incidents'] = 0
                context['metric_fatal'] = 0
                context['metric_fatalities'] = 0
                context['metric_ground'] = 0
                context['metric_split'] = "0 Fatal / 0 Non-Fatal"

            # 2. Top Aggregates (Aircraft)
            resp_ac = requests.get(f"{api_base}/aggregates/top-n", params={**params, 'category': 'aircraft_type', 'n': 5}, timeout=10)
            context['top_aircraft'] = json.dumps(resp_ac.json()) if resp_ac.status_code == 200 else "[]"

            # 3. Top Aggregates (Operator)
            resp_op = requests.get(f"{api_base}/aggregates/top-n", params={**params, 'category': 'operator', 'n': 5}, timeout=10)
            context['top_operators'] = json.dumps(resp_op.json()) if resp_op.status_code == 200 else "[]"

            # 4. Time Series (Line Chart)
            resp_time = requests.get(f"{api_base}/aggregates/over-time", params={**params, 'period': 'month'}, timeout=10)
            context['time_series'] = json.dumps(resp_time.json()) if resp_time.status_code == 200 else "[]"

            # 5. Heatmap (Bubble Chart format)
            # heatmap endpoint typically returns {dim1, dim2, count}
            resp_heat = requests.get(f"{api_base}/aggregates/heatmap", params={**params, 'dimension1': 'phase', 'dimension2': 'aircraft_type'}, timeout=15)
            context['heatmap'] = json.dumps(resp_heat.json()) if resp_heat.status_code == 200 else "[]"
            
            # 6. Hierarchy
            resp_hier = requests.get(f"{api_base}/aggregates/hierarchy", params={**params}, timeout=15)
            # Hierarchy endpoint might return a tree or list. 
            # If list of {key, count}, it works directly with our template.
            context['hierarchy'] = json.dumps(resp_hier.json()) if resp_hier.status_code == 200 else "[]"
            
            # 7. Data Table (Recent Incidents)
            # Reusing classification results endpoint or similar to get list
            resp_table = requests.get(f"{api_base}/classification-results", params={'skip': 0, 'limit': 10, 'evaluator_id': request.session.get('evaluator_id')}, timeout=10)
            
            if resp_table.status_code == 200:
                # Transform response to match template expectations
                # API returns list of {source_uid, origin_date, origin_operator, ...}
                raw_data = resp_table.json()
                table_data = []
                for item in raw_data:
                    table_data.append({
                        "id": item.get('id'),
                        "date": item.get('origin_date'),
                        "operator": item.get('origin_operator'),
                        "aircraft": item.get('origin_aircraft_type'),
                        "phase": item.get('origin_phase'),
                        "category": item.get('human_category') or item.get('llm_category') or 'UNK'
                    })
                context['table_data'] = table_data
            else:
                 context['table_data'] = []

        except requests.RequestException as e:
            messages.error(request, f"Error gathering dashboard data: {e}")
            # Ensure context has defaults
            context['metric_incidents'] = 0
            context['top_aircraft'] = "[]"
            context['top_operators'] = "[]"
            context['time_series'] = "[]"
            context['heatmap'] = "[]"
            context['hierarchy'] = "[]"
            context['table_data'] = []

        return render(request, 'evaluation_app/dashboard.html', context)

def dashboard_chart_data(request):
    """
    Proxy view to fetch interactive chart data from FastAPI
    Params: classifications (list), phases (list), period (str)
    """
    api_base = getattr(settings, 'FASTAPI_BASE_URL', 'http://localhost:8000')
    
    # Get parameters
    classifications = request.GET.getlist('classifications[]') # AJAX often sends arrays with []
    if not classifications:
         classifications = request.GET.getlist('classifications') # Standard GET
         
    phases = request.GET.getlist('phases[]')
    if not phases:
        phases = request.GET.getlist('phases')

    period = request.GET.get('period', 'month')
    
    params = {'period': period}
    if classifications: params['classifications'] = classifications
    if phases: params['phases'] = phases
    
    try:
        resp = requests.get(f"{api_base}/aggregates/classification-over-time", params=params, timeout=10)
        if resp.status_code == 200:
            from django.http import JsonResponse
            return JsonResponse(resp.json(), safe=False)
        else:
            from django.http import JsonResponse
            return JsonResponse({'error': f"API Error: {resp.text}"}, status=resp.status_code)
    except Exception as e:
        from django.http import JsonResponse
        return JsonResponse({'error': str(e)}, status=500)
