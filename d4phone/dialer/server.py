import os
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/d4/broadcast', methods=['POST'])
def trigger_commercial_broadcast():
    data = request.json or {}
    canopy_zone = data.get('canopy_zone', 'commercial_high_density')
    target_leads = data.get('lead_count', 0)
    
    return jsonify({
        "service": "d4-commercial-dialer",
        "status": "broadcast_initiated",
        "target_zone": canopy_zone,
        "leads_queued": target_leads,
        "outreach_channel": "openphone_broadcast"
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)