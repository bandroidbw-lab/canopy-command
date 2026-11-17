# --- PAGE 2: TENANT & D2 CONTROL CENTER ---
@app.route('/d6/tenants')
@login_required
def d6_tenants():
    """Renders the Tenant & D2 Control Center with singular focused vitals, callback dial count, and weather telemetry."""
    selected_id = request.args.get('contractor_id', CONTRACTORS_DIRECTORY[0]['id'])
    active_contractor = next((c for c in CONTRACTORS_DIRECTORY if c['id'] == selected_id), CONTRACTORS_DIRECTORY[0])
    
    # Mock weather telemetry for the regional corridor (e.g. Alamosa / Costilla County)
    weather_telemetry = {
        "condition": "High Pressure Front Rising",
        "barometer": "30.15 inHg",
        "trend": "Favorable for Field Work"
    }
    
    # Active callback list remaining dials counter
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