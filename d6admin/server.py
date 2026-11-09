import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/d6/admin/status', methods=['GET'])
def admin_status():
    return jsonify({
        "service": "d6-admin-dashboard",
        "status": "operational",
        "submodules": [
            "anchoraddress",
            "d2member",
            "onboarding",
            "reports",
            "searchhazards"
        ]
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)