import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Blueprint, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canopy-command-secure-production-key')

# --- IN-MEMORY TENANT REGISTRY (Mutable for D6 Admin Edits) ---
TENANTS_DB = [
    {
        "id": 1, 
        "name": "Apex Timberline", 
        "contractor_id": "CONT-AT01",
        "tier": "Enterprise Pilot", 
        "status": "active", 
        "billing": "Comped",
        "default_pricing": "Comped Pilot Tier"
    },
    {
        "id": 2, 
        "name": "Johnny Bailey", 
        "contractor_id": "CONT-JB01", 
        "tier": "D2 Operator", 
        "status": "active", 
        "billing": "Comped",
        "default_pricing": "$3.50 Ad-Hoc / Comped Core"
    }
]

# --- BLUEPRINT DEFINITIONS ---
d2_bp = Blueprint('d2', __name__, url_prefix='/d2')
d3_bp = Blueprint('d3', __name__, url_prefix='/d3')
d4_bp = Blueprint('d4', __name__, url_prefix='/d4')
d5_bp = Blueprint('d5', __name__, url_prefix='/d5')
d6_bp = Blueprint('d6', __name__, url_prefix='/d6')
report_bp = Blueprint('report', __name__, url_prefix='/report')

# --- D2 OPERATOR COMMAND CENTER ---
@d2_bp.route('/')
def d2_dashboard():
    contractor_id = request.args.get('contractor_id', 'CONT-JB01')
    return render_template('d2_exclusive_portal.html', contractor_id=contractor_id)

@d2_bp.route('/member-demo')
def d2_member_demo():
    return render_template('d2_exclusive_portal.html', contractor_id='DEMO-MEMBER')

# --- D3 FIELD BOARD ---
@d3_bp.route('/board')
def d3_board():
    token = request.args.get('token', '')
    return render_template('d3_field_board.html', token=token)

# --- D4 CONVERSION ESTIMATE HOOKS & REPORTING ---
@d4_bp.route('/webhook', methods=['POST'])
def d4_webhook():
    data = request.json or {}
    return jsonify({"status": "success", "message": "D4 conversion estimate logged", "payload": data}), 200

@d4_bp.route('/dashboard')
def d4_dashboard():
    return render_template('conversion_report.html', token="d4-master-active")

# --- D5 STANDALONE DIALER ---
@d5_bp.route('/workspace')
def d5_workspace():
    token = request.args.get('token', '')
    return render_template('d5_dialer_workspace.html', token=token)

# --- D6 ADMIN AUDITING & TENANT MANAGEMENT ---
@d6_bp.route('/dashboard')
def d6_dashboard():
    demo_boards = [
        {"name": "D2 Member Portal Demo", "url": "/d2/member-demo", "type": "Interactive Portal"},
        {"name": "D4 Conversion Estimator & Report", "url": "/d4/dashboard", "type": "Telemetry & PDF Hook"},
        {"name": "D3 Field Crew Board", "url": "/d3/board?token=master-demo", "type": "Secure Field Workspace"},
        {"name": "D5 Standalone Dialer", "url": "/d5/workspace?token=master-demo", "type": "Outreach Pilot Workspace"}
    ]
    return render_template('admin_dashboard.html', tenants=TENANTS_DB, demo_boards=demo_boards)

@d6_bp.route('/tenant/<int:tenant_id>/edit', methods=['GET', 'POST'])
def edit_tenant(tenant_id):
    tenant = next((t for t in TENANTS_DB if t["id"] == tenant_id), None)
    if not tenant:
        return "Tenant not found", 404
        
    if request.method == 'POST':
        tenant['name'] = request.form.get('name', tenant['name']).strip()
        tenant['contractor_id'] = request.form.get('contractor_id', tenant['contractor_id']).strip()
        tenant['tier'] = request.form.get('tier', tenant['tier']).strip()
        tenant['status'] = request.form.get('status', tenant['status']).strip()
        tenant['billing'] = request.form.get('billing', tenant['billing']).strip()
        tenant['default_pricing'] = request.form.get('default_pricing', tenant['default_pricing']).strip()
        return redirect('/d6/dashboard')
        
    return render_template('tenant_edit.html', tenant=tenant)

# --- REPORTLAB HAZARD REPORT VIEW ---
@report_bp.route('/view')
def report_view():
    token = request.args.get('token', '')
    return render_template('conversion_report.html', token=token)

# --- REGISTER ALL BLUEPRINTS ---
app.register_blueprint(d2_bp)
app.register_blueprint(d3_bp)
app.register_blueprint(d4_bp)
app.register_blueprint(d5_bp)
app.register_blueprint(d6_bp)
app.register_blueprint(report_bp)

# --- ROOT & SECURE LOGIN GATE ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def handle_login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    
    master_admin_user = os.environ.get('admin_username') or os.environ.get('ADMIN_USERNAME', 'admin')
    master_admin_pass = os.environ.get('admin_password') or os.environ.get('ADMIN_PASSWORD', 'canopy2026')
    
    if username == master_admin_user and password == master_admin_pass:
        return redirect('/d6/dashboard')
    elif username == 'contractor' and password == 'apex2026':
        return redirect('/d2/?contractor_id=CONT-JB01')
        
    return render_template('index.html', error=f"Invalid credentials for '{username}'. Access restricted.")

@app.route('/health')
def health_check():
    return jsonify({"status": "operational", "service": "canopy-command", "timestamp": datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)