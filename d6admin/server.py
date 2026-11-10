import os
from flask import Flask, render_template, jsonify, request

# Initialize Flask and point template_folder to the local templates directory
app = Flask(__name__, template_folder='templates')

# In-memory storage lists for auditing and reports across dashboards
SAVED_HAZARD_CRITERIA = []
SAVED_ANCHORS = []
SAVED_ADHOC_SCANS = []
SAVED_CLIENTS = []

@app.route('/', methods=['GET'])
def d6_home():
    # Renders d6admin/templates/index.html with links to all submodules
    return render_template('index.html')

@app.route('/d6/adhoc', methods=['GET'])
def adhoc_view():
    return render_template('adhoc.html')

@app.route('/d6/adhoc/search', methods=['POST'])
def adhoc_search_submit():
    address = request.form.get('address')
    notes = request.form.get('client_notes')
    scan_data = {"type": "adhoc", "address": address, "notes": notes}
    SAVED_ADHOC_SCANS.append(scan_data)
    return jsonify({"status": "success", "message": "Ad-hoc white glove hazard scan recorded successfully.", "data": scan_data})

@app.route('/d6/anchoraddress', methods=['GET'])
def anchor_address_view():
    return render_template('anchoraddress.html')

@app.route('/d6/anchoraddress/save', methods=['POST'])
def anchor_address_submit():
    name = request.form.get('anchor_name')
    coords = request.form.get('coordinates')
    anchor_data = {"type": "anchor", "name": name, "coordinates": coords}
    SAVED_ANCHORS.append(anchor_data)
    return jsonify({"status": "success", "message": "Anchor address saved successfully.", "data": anchor_data})

@app.route('/d6/searchhazards', methods=['GET'])
def search_hazards_view():
    return render_template('searchhazards.html')

@app.route('/d6/searchhazards/save', methods=['POST'])
def search_hazards_submit():
    contractor = request.form.get('contractor_id')
    radius = request.form.get('search_radius')
    tier = request.form.get('hazard_tier')
    criteria_data = {"type": "search_criteria", "contractor": contractor, "radius": radius, "tier": tier}
    SAVED_HAZARD_CRITERIA.append(criteria_data)
    return jsonify({"status": "success", "message": "Contractor search criteria saved and D2 queue loaded.", "data": criteria_data})

@app.route('/d6/onboarding', methods=['GET'])
def onboarding_view():
    return render_template('onboarding.html')

@app.route('/d6/onboarding/save', methods=['POST'])
def onboarding_submit():
    client = request.form.get('client_name')
    address = request.form.get('address')
    zip_code = request.form.get('zip')
    comp_leads = request.form.get('comp_leads')
    trial = request.form.get('trial_length')
    client_data = {"type": "client", "client": client, "address": address, "zip": zip_code, "comp_leads": comp_leads, "trial_days": trial}
    SAVED_CLIENTS.append(client_data)
    return jsonify({"status": "success", "message": "Client onboarding profile saved successfully.", "data": client_data})

@app.route('/d6/reports', methods=['GET'])
def reports_view():
    # Reports aggregates and returns all data across every dashboard and submodule
    comprehensive_report = {
        "module": "reports",
        "status": "active",
        "total_adhoc_scans": len(SAVED_ADHOC_SCANS),
        "total_anchor_addresses": len(SAVED_ANCHORS),
        "total_contractor_criteria": len(SAVED_HAZARD_CRITERIA),
        "total_onboarded_clients": len(SAVED_CLIENTS),
        "audit_logs": {
            "adhoc_scans": SAVED_ADHOC_SCANS,
            "anchor_addresses": SAVED_ANCHORS,
            "search_criteria": SAVED_HAZARD_CRITERIA,
            "clients": SAVED_CLIENTS
        }
    }
    return jsonify(comprehensive_report)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)