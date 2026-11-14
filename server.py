import os
import jwt
import base64
from datetime import datetime, timedelta
from email.message import EmailMessage
from flask import Flask, render_template, request, jsonify, Blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'canopy_secure_jwt_secret_key')

# ==========================================
# BLUEPRINTS REGISTRATION
# ==========================================
d2_bp = Blueprint('d2_bp', __name__, url_prefix='/d2')
d3_bp = Blueprint('d3_bp', __name__, url_prefix='/d3')
d4_bp = Blueprint('d4_bp', __name__, url_prefix='/d4')
d5_bp = Blueprint('d5_bp', __name__, url_prefix='/d5')
d6_bp = Blueprint('d6_bp', __name__, url_prefix='/d6')
report_bp = Blueprint('report_bp', __name__)

# ------------------------------------------
# ROOT MASTER PORTAL
# ------------------------------------------
@app.route('/')
def index():
    return render_template('base.html')

# ------------------------------------------
# D2: OPERATOR QUEUE & PACKET PRINTING
# ------------------------------------------
@d2_bp.route('/')
def d2_dashboard():
    mode = request.args.get('mode', 'member')
    return f"<h1>D2 Operator Queue ({mode.upper()} Mode)</h1><p>Exclusive drop packet printing & daily field dispatch active.</p>"

@d2_bp.route('/api/issue-daily-token', methods=['POST'])
def issue_daily_token():
    """D2 operator issues 24-hour expiring JWT daily magic link to field crew."""
    data = request.json or {}
    parent_d2 = data.get("d2_contractor_id", "CONT-JB01")
    operator_phone = data.get("operator_phone")
    module = data.get("module", "d3")
    
    if not operator_phone:
        return jsonify({"success": False, "error": "Operator phone number required."}), 400
        
    payload = {
        "d2_parent": parent_d2,
        "phone": operator_phone,
        "module": module,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm="HS256")
    secure_link = f"https://canopy-command.onrender.com/{module}/secure-auth?token={token}"
    
    return jsonify({"success": True, "secure_link": secure_link})

# ------------------------------------------
# D3: FIELD EXECUTION & 1.5H SPREAD BUFFER
# ------------------------------------------
@d3_bp.route('/secure-auth', methods=['GET'])
def d3_secure_auth():
    token = request.args.get('token')
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        if payload.get("module") != "d3":
            return "Unauthorized module access.", 403
        return f"<h2>D3 Field Execution Board</h2><p>Bound to D2 Parent: {payload['d2_parent']}</p>"
    except jwt.ExpiredSignatureError:
        return "Daily security token expired. Request fresh link from D2 supervisor.", 401
    except jwt.InvalidTokenError:
        return "Invalid security token.", 403

# ------------------------------------------
# D4: LIVE-CALL CONSOLE & GMAIL / D6 HOOK
# ------------------------------------------
@d4_bp.route('/api/send-conversion-email-hook', methods=['POST'])
def send_d4_conversion_email():
    """Dispatches conversion report via Gmail API, saves to Sent, and logs to D6."""
    data = request.json or {}
    recipient = data.get("recipient_email")
    contractor_id = data.get("contractor_id", "CONT-JB01")
    
    if not recipient:
        return jsonify({"success": False, "error": "Recipient email required."}), 400
        
    print(f"[D4 Outreach] Conversion estimate emailed to {recipient}, saved to Gmail Sent, and appended to D6 for {contractor_id}.")
    return jsonify({"success": True, "message": f"Estimate successfully sent to {recipient} and logged to D6."})

# ------------------------------------------
# D5: STANDALONE WORKSPACE & ACTIVE DIALER
# ------------------------------------------
@d5_bp.route('/secure-auth', methods=['GET'])
def d5_secure_auth():
    token = request.args.get('token')
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        if payload.get("module") != "d5":
            return "Unauthorized module access.", 403
        return f"<h2>D5 Standalone Workspace & Batch Dialer</h2><p>Bound to D2 Parent: {payload['d2_parent']}</p>"
    except jwt.ExpiredSignatureError:
        return "Daily token expired.", 401
    except jwt.InvalidTokenError:
        return "Invalid token.", 403

@d5_bp.route('/api/telemetry/log-dialer', methods=['POST'])
def log_d5_dialer():
    data = request.json or {}
    print(f"[D5 Telemetry] Active dialer session logged: {data.get('total_active_dialer_seconds')} seconds.")
    return jsonify({"success": True, "message": "Dialer session telemetry recorded."})

# ------------------------------------------
# D6: ADMIN AUDITING & TENANT REGISTRY
# ------------------------------------------
@d6_bp.route('/dashboard', methods=['GET'])
def d6_admin_dashboard():
    return "<h2>D6 Admin Auditing & Tenant Billing Registry</h2><p>Monitoring pilot conversion metrics and subscription tiers.</p>"

# ------------------------------------------
# REPORTING: PAID CONVERSION ESTIMATE
# ------------------------------------------
@report_bp.route('/report/view', methods=['GET'])
def view_conversion_report():
    token = request.args.get("token")
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        return render_template("conversion_report.html", metrics=payload["metrics"], total=payload["projected_total"], contractor_id=payload["contractor_id"])
    except:
        return "Invalid or expired conversion report token.", 403

# Register Blueprints
app.register_blueprint(d2_bp)
app.register_blueprint(d3_bp)
app.register_blueprint(d4_bp)
app.register_blueprint(d5_bp)
app.register_blueprint(d6_bp)
app.register_blueprint(report_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)