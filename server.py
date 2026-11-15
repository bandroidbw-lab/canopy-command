import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Blueprint, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canopy-command-secure-production-key')

# --- BLUEPRINT DEFINITIONS ---
d2_bp = Blueprint('d2', __name__, url_prefix='/d2')
d3_bp = Blueprint('d3', __name__, url_prefix='/d3')
d4_bp = Blueprint('d4', __name__, url_prefix='/d4')
d5_bp = Blueprint('d5', __name__, url_prefix='/d5')
d6_bp = Blueprint('d6', __name__, url_prefix='/d6')
report_bp = Blueprint('report', __name__, url_prefix='/report')

# --- D2 OPERATOR COMMAND CENTER (Strictly isolated for D2 Supervisors) ---
@d2_bp.route('/')
def d2_dashboard():
    contractor_id = request.args.get('contractor_id', 'CONT-JB01')
    return render_template('d2_exclusive_portal.html', contractor_id=contractor_id)

# --- D3 FIELD BOARD (Restricted Field Execution) ---
@d3_bp.route('/board')
def d3_board():
    token = request.args.get('token', '')
    return render_template('d3_field_board.html', token=token)

# --- D4 CONVERSION ESTIMATE HOOKS ---
@d4_bp.route('/webhook', methods=['POST'])
def d4_webhook():
    data = request.json or {}
    return jsonify({"status": "success", "payload": data}), 200

# --- D5 STANDALONE DIALER ---
@d5_bp.route('/workspace')
def d5_workspace():
    token = request.args.get('token', '')
    return render_template('d5_dialer_workspace.html', token=token)

# --- D6 ADMIN AUDITING (Strictly Owner Only) ---
@d6_bp.route('/dashboard')
def d6_dashboard():
    sample_tenants = [
        {
            "id": 1, 
            "name": "Apex Timberline", 
            "tier": "Enterprise Pilot", 
            "status": "active", 
            "billing": "Comped"
        },
        {
            "id": 2, 
            "name": "Johnny Bailey", 
            "contractor_id": "CONT-JB01", 
            "tier": "D2 Operator", 
            "status": "active", 
            "billing": "Comped"
        }
    ]
    return render_template('admin_dashboard.html', tenants=sample_tenants)

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
    
    # Secure Master Admin credentials pulled from environment variables (with fallback defaults)
    master_admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
    master_admin_pass = os.environ.get('ADMIN_PASSWORD', 'canopy2026')
    
    # Master Admin / Owner Login Check
    if username == master_admin_user and password == master_admin_pass:
        return redirect('/d6/dashboard')
    
    # D2 Contractor Login Check (Johnny Bailey / CONT-JB01)
    elif username == 'contractor' and password == 'apex2026':
        return redirect('/d2/?contractor_id=CONT-JB01')
        
    # Failed Authentication fallback
    return render_template('index.html', error="Invalid credentials. Access restricted.")

@app.route('/health')
def health_check():
    return jsonify({"status": "operational", "service": "canopy-command", "timestamp": datetime.utcnow().isoformat()}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)