import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'canopy-command-secret-key-2026')

# --- IN-MEMORY DATA REGISTRIES (Production syncs to PostgreSQL / Supabase) ---

CONTRACTORS_DIRECTORY = [
    {
        "id": "CONT-JB01", 
        "name": "Johnny Bailey", 
        "tier": "White-Glove ($299/mo)", 
        "status": "Paid Enterprise", 
        "usage_score": 95, 
        "region": "Alamosa, CO", 
        "phone": "+17195550191", 
        "queue_type": "white_glove",
        "balance": 200.00,
        "stripe_payment_method_id": "pm_card_visa_tokenized"
    },
    {
        "id": "CONT-AT01", 
        "name": "Apex Timberline", 
        "tier": "White-Glove ($299/mo)", 
        "status": "Paid Enterprise", 
        "usage_score": 88, 
        "region": "Blanca, CO", 
        "phone": "+17195550192", 
        "queue_type": "white_glove",
        "balance": 175.00,
        "stripe_payment_method_id": "pm_card_mastercard_tokenized"
    },
    {
        "id": "CONT-NC02", 
        "name": "Blue Ridge Canopy", 
        "tier": "Pilot Member", 
        "status": "Active Pilot (Comped)", 
        "usage_score": 74, 
        "region": "Asheville, NC", 
        "phone": "+18285550143", 
        "queue_type": "pilot_usage",
        "balance": 50.00,
        "stripe_payment_method_id": None
    },
    {
        "id": "CONT-SL03", 
        "name": "San Luis Valley Woods", 
        "tier": "Pilot Member", 
        "status": "Unpaid Pilot", 
        "usage_score": 42, 
        "region": "Costilla County, CO", 
        "phone": "+17195550188", 
        "queue_type": "pilot_usage",
        "balance": 0.00,
        "stripe_payment_method_id": None
    },
    {
        "id": "CONT-BC04", 
        "name": "Backcountry Harvest", 
        "tier": "Broadcaster Callback", 
        "status": "Pending Callback", 
        "usage_score": 60, 
        "region": "Bailey, CO", 
        "phone": "+13035550125", 
        "queue_type": "broadcaster_callback",
        "balance": 25.00,
        "stripe_payment_method_id": None
    }
]

USAGE_AUDIT_LOGS = [
    {"timestamp": "2026-11-17 07:30:12", "contractor_id": "CONT-JB01", "action": "D3_DOOR_DROP_SAVED", "details": "Parcel 70226200 disposition updated."},
    {"timestamp": "2026-11-17 07:30:15", "contractor_id": "CONT-JB01", "action": "D2_PROGRESSION_VIEW", "details": "Loaded printable report view."},
    {"timestamp": "2026-11-17 07:31:02", "contractor_id": "CONT-AT01", "action": "D5_HAZARD_SCAN", "details": "Ad-hoc technical screening executed ($3.50 unit)."}
]

# Live Scoreboard Telemetry driven dynamically from logs
DAILY_TELEMETRY = {
    "calls_today": 42,
    "press_ones": 7,
    "converted_pilots": 3,
    "retainer_revenue": 897.00
}


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    if username == os.environ.get('admin_username', 'admin') and password == os.environ.get('admin_password', 'canopy2026'):
        session['logged_in'] = True
        session['is_admin'] = True
        return redirect('/d6/dashboard')
    return render_template('index.html', error="Invalid credentials.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- THE 6 ADMIN BLUEPRINT PAGES ---

@app.route('/d6/dashboard')
@login_required
def d6_dashboard():
    pilot_queue = sorted([c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'pilot_usage'], key=lambda x: x['usage_score'], reverse=True)
    white_glove_queue = [c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'white_glove']
    callback_queue = [c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'broadcaster_callback']
    
    return render_template('admin_dashboard.html', 
                           white_glove=white_glove_queue,
                           pilots=pilot_queue,
                           callbacks=callback_queue,
                           telemetry=DAILY_TELEMETRY,
                           directory=CONTRACTORS_DIRECTORY)

@app.route('/d6/tenants')
@login_required
def d6_tenants():
    selected_id = request.args.get('contractor_id', CONTRACTORS_DIRECTORY[0]['id'])
    active_contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == selected_id), CONTRACTORS_DIRECTORY[0])
    tenant_logs = [log for log in USAGE_AUDIT_LOGS if log['contractor_id'] == active_contractor['id']]
    return render_template('admin_tenants.html', directory=CONTRACTORS_DIRECTORY, active_contractor=active_contractor, tenant_logs=tenant_logs)

@app.route('/d6/phonebook')
@login_required
def d6_phonebook():
    return render_template('admin_phonebook.html', directory=CONTRACTORS_DIRECTORY)

@app.route('/d6/broadcaster')
@login_required
def d6_broadcaster():
    return render_template('admin_broadcaster.html')

@app.route('/d6/pricing')
@login_required
def d6_pricing():
    return render_template('admin_pricing.html')

@app.route('/d6/reports')
@login_required
def d6_reports():
    return render_template('admin_reports.html', logs=USAGE_AUDIT_LOGS, telemetry=DAILY_TELEMETRY)


# --- API ENDPOINTS ---

@app.route('/d6/global-search', methods=['GET'])
@login_required
def global_search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({"status": "success", "results": []})
    matches = [c for c in CONTRACTORS_DIRECTORY if query in c['name'].lower() or query in c['id'].lower() or query in c['region'].lower() or query in c['phone']]
    return jsonify({"status": "success", "results": matches})

@app.route('/d6/convert-pilot', methods=['POST'])
@login_required
def convert_pilot():
    data = request.get_json() or {}
    contractor_id = data.get('contractor_id')
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), None)
    if not contractor:
        return jsonify({"status": "error", "message": "Contractor not found."}), 404
    contractor['tier'] = "Self-Managed ($5.00 Unit - Retainer Waived)"
    contractor['status'] = "Paid Enterprise (Self-Run)"
    DAILY_TELEMETRY['converted_pilots'] += 1
    USAGE_AUDIT_LOGS.append({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "contractor_id": contractor_id, "action": "PILOT_CONVERTED", "details": "Retainer waived, $5.00 baseline active."})
    return jsonify({"status": "success", "message": f"Successfully converted {contractor['name']}!", "updated_contractor": contractor})

@app.route('/d6/doctor-screen', methods=['POST'])
@login_required
def doctor_screen():
    data = request.get_json() or {}
    contractor_id = data.get('contractor_id')
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), None)
    if not contractor:
        return jsonify({"status": "error", "message": "Not found."}), 404
    contractor['status'] = data.get('status', contractor['status'])
    contractor['tier'] = data.get('tier', contractor['tier'])
    contractor['balance'] = float(data.get('balance', contractor['balance']))
    return jsonify({"status": "success", "message": "Override saved."})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)