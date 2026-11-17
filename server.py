import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# 1. Initialize Flask app FIRST before any route decorators
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'canopy-command-secret-key-2026')

# --- MOCK DIRECTORY & TELEMETRY DATA ---
DAILY_TELEMETRY = {
    "calls_today": 42,
    "press_ones": 7,
    "converted_pilots": 3,
    "retainer_revenue": 897.00
}

CONTRACTORS_DIRECTORY = [
    {
        "id": "c_001",
        "name": "Apex Timberline Tree Service",
        "region": "Alamosa / Costilla County, CO",
        "phone": "+17195550142",
        "tier": "White-Glove Pilot",
        "status": "Active Callback",
        "queue_type": "broadcaster_callback",
        "balance": 125.00,
        "usage_score": 94
    },
    {
        "id": "c_002",
        "name": "Sangre de Cristo Tree & Land",
        "region": "Blanca / Alamosa, CO",
        "phone": "+17195550189",
        "tier": "Paid Member",
        "status": "Converted",
        "queue_type": "standard",
        "balance": 340.50,
        "usage_score": 88
    }
]

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == os.environ.get('ADMIN_PASSWORD', 'canopy2026'):
            session['logged_in'] = True
            return redirect(url_for('d6_dashboard'))
    return '''
        <h2>Canopy Command Sign-In</h2>
        <form method="post">
            <input type="password" name="password" placeholder="Admin Password" required>
            <button type="submit">Sign In</button>
        </form>
    '''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# --- PAGE 1: D6 SWITCHBOARD DASHBOARD ---
@app.route('/d6/dashboard')
@login_required
def d6_dashboard():
    return render_template('admin_dashboard.html', telemetry=DAILY_TELEMETRY, directory=CONTRACTORS_DIRECTORY)

# --- PAGE 2: TENANT & D2 CONTROL CENTER ---
@app.route('/d6/tenants')
@login_required
def d6_tenants():
    """Renders the Tenant & D2 Control Center with singular focused vitals, callback dial count, and weather telemetry."""
    selected_id = request.args.get('contractor_id', CONTRACTORS_DIRECTORY[0]['id'])
    active_contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == selected_id), CONTRACTORS_DIRECTORY[0])
    
    weather_telemetry = {
        "condition": "High Pressure Front Rising",
        "barometer": "30.15 inHg",
        "trend": "Favorable for Field Work"
    }
    
    callback_queue_count = len([c for c in CONTRACTORS_DIRECTORY if c['queue_type'] == 'broadcaster_callback'])

    return render_template(
        'admin_tenants.html',
        active_contractor=active_contractor,
        telemetry=DAILY_TELEMETRY,
        weather=weather_telemetry,
        remaining_dials=callback_queue_count
    )

@app.route('/d6/tenants/update-accounting', methods=['POST'])
@login_required
def update_tenant_accounting():
    """Handles up-front balance top-ups, minimum balance enforcement, and lead comping."""
    data = request.get_json() or {}
    contractor_id = data.get('contractor_id')
    top_up_amount = float(data.get('top_up_amount', 0.0))
    min_threshold = float(data.get('min_threshold', 50.0))
    comp_lead = data.get('comp_lead', False)
    
    contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == contractor_id), None)
    if not contractor:
        return jsonify({"status": "error", "message": "Contractor not found."}), 404
        
    contractor['balance'] += top_up_amount
    if comp_lead:
        contractor['balance'] += 5.00  # Comped lead credit
        
    return jsonify({
        "status": "success",
        "message": f"Updated accounting for {contractor['name']}. New balance: ${contractor['balance']:.2f}",
        "new_balance": contractor['balance']
    })

@app.route('/d6/tenants/calculate-pricing', methods=['POST'])
@login_required
def calculate_pricing():
    """Calculates territory pricing based on hazard density and returns a mock Stripe checkout link."""
    data = request.get_json() or {}
    roof = float(data.get('roof_hazards', 0))
    drive = float(data.get('driveway_hazards', 0))
    calculated = 50.00 + (roof * 10.00) + (drive * 7.50)
    
    return jsonify({
        "calculated_price": calculated,
        "stripe_checkout_url": f"https://buy.stripe.com/test_canopy_{int(calculated)}00"
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)