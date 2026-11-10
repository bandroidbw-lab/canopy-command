import os
from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

@app.route('/', methods=['GET'])
def d6_home():
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Canopy Command - D6 Admin Hub</title>
            <style>
                body { font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 40px; }
                .card { background: #1e293b; padding: 25px; border-radius: 8px; max-width: 600px; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
                h1 { color: #38bdf8; }
                ul { list-style: none; padding: 0; }
                li { background: #334155; margin: 10px 0; padding: 12px; border-radius: 4px; display: flex; justify-content: space-between; }
                a { color: #38bdf8; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>D6 Admin & Operations Hub</h1>
                <p>Status: <span style="color: #4ade80;">Operational</span></p>
                <h3>Active Submodules:</h3>
                <ul>
                    <li><span>Anchor Address</span> <a href="/d6/anchoraddress">Open</a></li>
                    <li><span>Search Hazards</span> <a href="/d6/searchhazards">Open</a></li>
                    <li><span>Reports</span> <a href="/d6/reports">Open</a></li>
                    <li><span>Onboarding</span> <a href="/d6/onboarding">Open</a></li>
                    <li><span>Ad-Hoc Operations</span> <a href="/d6/adhoc">Open</a></li>
                </ul>
            </div>
        </body>
        </html>
    """)

@app.route('/d6/anchoraddress', methods=['GET'])
def anchor_address():
    return jsonify({"module": "anchoraddress", "status": "active", "path": "d6admin/anchoraddress"})

@app.route('/d6/searchhazards', methods=['GET'])
def search_hazards():
    return jsonify({"module": "searchhazards", "status": "active", "path": "d6admin/searchhazards"})

@app.route('/d6/reports', methods=['GET'])
def reports():
    return jsonify({"module": "reports", "status": "active", "path": "d6admin/reports"})

@app.route('/d6/onboarding', methods=['GET'])
def onboarding():
    return jsonify({"module": "onboarding", "status": "active", "path": "d6admin/onboarding"})

@app.route('/d6/adhoc', methods=['GET'])
def adhoc():
    return jsonify({"module": "adhoc", "status": "active", "path": "d6admin/adhoc"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)