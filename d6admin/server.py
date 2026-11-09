import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

@app.route('/')
def d6_dashboard():
    try:
        # Fallback inline HTML rendering if templates folder is missing
        return render_template_string("""
            <!DOCTYPE html>
            <html>
            <head><title>D6 Admin Hub</title></head>
            <body style="font-family: Arial; background: #0f172a; color: #fff; padding: 40px;">
                <h1>D6 Admin & Operations Hub</h1>
                <p>Status: Operational</p>
                <ul>
                    <li>anchoraddress</li>
                    <li>d2member</li>
                    <li>onboarding</li>
                    <li>reports</li>
                    <li>searchhazards</li>
                </ul>
            </body>
            </html>
        """)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/d6/admin/status', methods=['GET'])
def admin_status():
    return jsonify({
        "service": "d6-admin-hub",
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