import os
from datetime import datetime
from flask import Flask, render_template, jsonify, request, Blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canopy-command-secure-production-key')

# --- BLUEPRINT DEFINITIONS ---
d2_bp = Blueprint('d2', __name__, url_prefix='/d2')
d3_bp = Blueprint('d3', __name__, url_prefix='/d3')
d4_bp = Blueprint('d4', __name__, url_prefix='/d4')
d5_bp = Blueprint('d5', __name__, url_prefix='/d5')
d6_bp = Blueprint('d6', __name__, url_prefix='/d6')
report_bp = Blueprint('report', __name__, url_prefix='/report')

# --- D2 OPERATOR QUEUE & WORKFLOWS ---
@d2_bp.route('/')
def d2_queue():
    contractor_id = request.args.get('contractor_id', 'CONT-JB01')
    return render_template('d2_queue.html', contractor_id=contractor_id)

# --- D3 FIELD BOARD & AUTH ---
@d3_bp.route('/secure-auth')
def d3_auth():
    token = request.args.get('token', '')
    return render_template('d3_auth.html', token=token, status="active")

# --- D4 OUTREACH & CONVERSION HOOKS ---
@d4_bp.route('/webhook', methods=['POST'])
def d4_webhook():
    data = request.json or {}
    return jsonify({
        "status": "success",
        "message": "D4 conversion estimate email hook logged",
        "payload": data
    }), 200

# --- D5 STANDALONE DIALER & SINGLE SCANS ---
@d5_bp.route('/secure-auth')
def d5_auth():
    token = request.args.get('token', '')
    return render_template('d5_auth.html', token=token, rate="$3.50 flat")

# --- D6 ADMIN AUDITING & BILLING DASHBOARD ---
@d6_bp.route('/dashboard')
def d6_dashboard():
    sample_tenants = [
        {"id": 1, "name": "Apex Timberline", "tier": "Winter Alpha Pilot", "status": "active", "billing": "Comped"}
    ]
    return render_template('admin_dashboard.html', tenants=sample_tenants)

# --- REPORTLAB HAZARD REPORT & CONVERSION VIEW ---
@report_bp.route('/view')
def report_view():
    token = request.args.get('token', '')
    return render_template('converson_report.html', token=token)

# --- REGISTER ALL BLUEPRINTS ---
app.register_blueprint(d2_bp)
app.register_blueprint(d3_bp)
app.register_blueprint(d4_bp)
app.register_blueprint(d5_bp)
app.register_blueprint(d6_bp)
app.register_blueprint(report_bp)

# --- ROOT & HEALTH CHECK ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """System health check endpoint for Render uptime monitoring."""
    return jsonify({
        "status": "operational",
        "service": "canopy-command",
        "timestamp": datetime.utcnow().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)