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
    {"timestamp": "2026-11-16 14:30:12", "contractor_id": "CONT-JB01", "action": "D3_DOOR_DROP_SAVED", "details": "Parcel 70226200 disposition updated."},
    {"timestamp": "2026-11-16 14:30:15", "contractor_id": "CONT-JB01", "action": "D2_PROGRESSION_VIEW", "details": "Loaded printable report view."},
    {"timestamp": "2026-11-16 14:31:02", "contractor_id": "CONT-AT01", "action": "D5_HAZARD_SCAN", "details": "Ad-hoc technical screening executed ($3.50 unit)."}
]

LEDGER_TRANSACTIONS = [
    {"tx_id": "TX-9001", "tenant_id": "CONT-JB01", "timestamp": "2026-11-16 08:30:00", "type": "RELOAD", "amount": 200.00, "desc": "Initial Monthly Pre-Funded White-Glove Retainer"}
]


# --- AUTHENTICATION DECORATOR ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


# --- CORE & AUTH ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    master_admin_user = os.environ.get('admin_username', 'admin')
    master_admin_pass = os.environ.get('admin_password', 'canopy2026')
    
    if username == master_admin_user and password == master_admin_pass:
        session['logged_in'] = True
        session['is_admin'] = True
        return redirect('/d6/dashboard')
    elif username == 'contractor' and password == 'apex2026':
        session['logged_in'] = True
        session['is_admin'] = False
        return redirect('/d2/?contractor_id=CONT-JB01')
        
    return render_template('index.html', error="Invalid credentials. Access restricted.")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# --- D2 OPERATOR & PROGRESSION PORTAL ---
@app.route('/d2/')
@login_required
def d2_dashboard():
    contractor_id = request.args.get('contractor_id', 'CONT-JB01')
    mode = request.args.get('mode', 'standard')
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), CONTRACTORS_DIRECTORY[0])
    return render_template('d2_portal.html', contractor=contractor, demo_mode=(mode == 'demo'))


# --- D3 FIELD CANVASSING BOARD ---
@app.route('/d3/board')
@login_required
def d3_board():
    return render_template('d3_board.html')


# --- D5 TECHNICAL STORM HAZARD SCREENING WORKSPACE ---
@app.route('/d5/workspace')
@login_required
def d5_workspace():
    return render_template('d5_workspace.html')


# --- D6 MASTER SWITCHBOARD & CUSTOMER SERVICE ROUTES ---
@app.route('/d6/dashboard')
@login_required
def d6_dashboard():
    pilot_queue = sorted([c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'pilot_usage'], key=lambda x: x['usage_score'], reverse=True)
    white_glove_queue = [c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'white_glove']
    callback_queue = [c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'broadcaster_callback']
    
    return render_template('admin_dashboard.html', 
                           white_glove=white_glove_queue,
                           pilots=pilot_queue,
                           callbacks=callback_queue)

@app.route('/d6/global-search', methods=['GET'])
@login_required
def global_search():
    query = request.args.get('q', '').strip().lower()
    if not query:
        return jsonify({"status": "success", "results": []})
    
    matches = []
    for c in CONTRACTORS_DIRECTORY:
        if query in c['name'].lower() or query in c['id'].lower() or query in c['region'].lower() or query in c['phone']:
            c_logs = [log for log in USAGE_AUDIT_LOGS if log['contractor_id'] == c['id']]
            matches.append({
                **c,
                "recent_activity": c_logs[-5:] if c_logs else [{"timestamp": "N/A", "action": "No recent telemetry", "details": ""}]
            })
            
    return jsonify({"status": "success", "results": matches})

@app.route('/d6/doctor-screen', methods=['POST'])
@login_required
def doctor_screen():
    data = request.get_json() or {}
    contractor_id = data.get('contractor_id')
    new_status = data.get('status')
    new_balance = data.get('balance')
    
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), None)
    if not contractor:
        return jsonify({"status": "error", "message": "Contractor record not found."}), 404
        
    if new_status:
        contractor['status'] = new_status
    if new_balance is not None:
        contractor['balance'] = float(new_balance)
        
    return jsonify({
        "status": "success", 
        "message": f"Successfully doctored record for {contractor['name']}.",
        "updated_record": contractor
    })

@app.route('/d6/save-card-token', methods=['POST'])
@login_required
def save_card_token():
    data = request.get_json() or {}
    contractor_id = data.get('contractor_id')
    payment_method_id = data.get('payment_method_id', '').strip()
    
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), None)
    if not contractor:
        return jsonify({"status": "error", "message": "Contractor record not found."}), 404
        
    contractor['stripe_payment_method_id'] = payment_method_id
    contractor['status'] = "Paid Enterprise"
    
    return jsonify({
        "status": "success",
        "message": f"Successfully vaulted card-on-file ({payment_method_id}) for {contractor['name']}.",
        "updated_contractor": contractor
    })

@app.route('/d6/calculate-zip-pricing', methods=['POST'])
@login_required
def calculate_zip_pricing():
    data = request.get_json() or {}
    zip_code = data.get('zip_code', '').strip()
    projected_leads = int(data.get('projected_leads', 15))
    roof_hazards = int(data.get('roof_hazards', 3))
    driveway_hazards = int(data.get('driveway_hazards', 2))
    
    base_price = 50.00
    lead_component = projected_leads * 2.50
    hazard_component = (roof_hazards + driveway_hazards) * 5.00
    total_price = max(50.00, base_price + lead_component + hazard_component)
    
    return jsonify({
        "status": "success",
        "zip_code": zip_code,
        "projected_leads": projected_leads,
        "calculated_price": round(total_price, 2)
    })

@app.route('/d6/create-stripe-checkout', methods=['POST'])
@login_required
def create_stripe_checkout():
    data = request.get_json() or {}
    zip_code = data.get('zip_code')
    amount = float(data.get('amount', 50.00))
    checkout_url = f"https://checkout.stripe.com/pay/cs_live_sample_zip_{zip_code}"
    return jsonify({
        "status": "success",
        "checkout_url": checkout_url,
        "amount": amount,
        "zip_code": zip_code
    })

@app.route('/d6/send-demo-link', methods=['POST'])
@login_required
def send_demo_link():
    data = request.get_json() or {}
    phone = data.get('phone', '').strip()
    board_name = data.get('board_name', 'Demo Board')
    board_url = data.get('url', '')
    
    return jsonify({
        "status": "success", 
        "message": f"Demo link for {board_name} successfully texted to {phone}."
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)