import os
from flask import Flask, render_template, jsonify, request, redirect, url_for

# Initialize Flask and point template_folder to the local templates directory
app = Flask(__name__, template_folder='templates')

# In-memory storage lists for auditing and reports across dashboards
SAVED_HAZARD_CRITERIA = []
SAVED_ANCHORS = []
SAVED_ADHOC_SCANS = []
SAVED_CLIENTS = []

@app.route('/', methods=['GET'])
def d6_home():
    return render_template('index.html')

@app.route('/d6/adhoc', methods=['GET'])
def adhoc_view():
    return render_template('adhoc.html')

@app.route('/d6/adhoc/search', methods=['POST'])
def adhoc_search_submit():
    address = request.form.get('address', 'N/A')
    notes = request.form.get('client_notes', 'N/A')
    scan_data = {"type": "adhoc", "address": address, "notes": notes}
    SAVED_ADHOC_SCANS.append(scan_data)
    return redirect(url_for('reports_view'))

@app.route('/d6/anchoraddress', methods=['GET'])
def anchor_address_view():
    return render_template('anchoraddress.html')

@app.route('/d6/anchoraddress/save', methods=['POST'])
def anchor_address_submit():
    name = request.form.get('anchor_name', 'N/A')
    coords = request.form.get('coordinates', 'N/A')
    anchor_data = {"type": "anchor", "name": name, "coordinates": coords}
    SAVED_ANCHORS.append(anchor_data)
    return redirect(url_for('reports_view'))

@app.route('/d6/searchhazards', methods=['GET'])
def search_hazards_view():
    return render_template('searchhazards.html')

@app.route('/d6/searchhazards/save', methods=['POST'])
def search_hazards_submit():
    contractor = request.form.get('contractor_id', 'N/A')
    radius = request.form.get('search_radius', 'N/A')
    tier = request.form.get('hazard_tier', 'N/A')
    criteria_data = {"type": "search_criteria", "contractor": contractor, "radius": radius, "tier": tier}
    SAVED_HAZARD_CRITERIA.append(criteria_data)
    return redirect(url_for('reports_view'))

@app.route('/d6/onboarding', methods=['GET'])
def onboarding_view():
    return render_template('onboarding.html')

@app.route('/d6/onboarding/save', methods=['POST'])
def onboarding_submit():
    client = request.form.get('client_name', 'N/A')
    address = request.form.get('address', 'N/A')
    zip_code = request.form.get('zip', 'N/A')
    comp_leads = request.form.get('comp_leads', '0')
    trial = request.form.get('trial_length', '0')
    client_data = {"type": "client", "client": client, "address": address, "zip": zip_code, "comp_leads": comp_leads, "trial_days": trial}
    SAVED_CLIENTS.append(client_data)
    return redirect(url_for('reports_view'))

@app.route('/d6/reports', methods=['GET'])
def reports_view():
    return render_template('reports.html', 
                           adhoc_scans=SAVED_ADHOC_SCANS,
                           anchors=SAVED_ANCHORS,
                           criteria=SAVED_HAZARD_CRITERIA,
                           clients=SAVED_CLIENTS,
                           total_adhoc=len(SAVED_ADHOC_SCANS),
                           total_anchor=len(SAVED_ANCHORS),
                           total_criteria=len(SAVED_HAZARD_CRITERIA),
                           total_clients=len(SAVED_CLIENTS))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)