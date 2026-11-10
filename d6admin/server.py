import os
from flask import Flask, render_template, jsonify

# Initialize Flask and point template_folder to the local templates directory
app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET'])
def d6_home():
    # Renders d6admin/templates/index.html with links to all submodules
    return render_template('index.html')

@app.route('/d6/adhoc', methods=['GET'])
def adhoc_view():
    # Renders d6admin/templates/adhoc.html for single-address white glove hazard searches
    return render_template('adhoc.html')

@app.route('/d6/anchoraddress', methods=['GET'])
def anchor_address_view():
    # Renders d6admin/templates/anchoraddress.html for anchor parcel management
    return render_template('anchoraddress.html')

@app.route('/d6/searchhazards', methods=['GET'])
def search_hazards_view():
    return jsonify({"module": "searchhazards", "status": "active", "description": "Search hazards submodule"})

@app.route('/d6/reports', methods=['GET'])
def reports_view():
    return jsonify({"module": "reports", "status": "active", "description": "Reports submodule"})

@app.route('/d6/onboarding', methods=['GET'])
def onboarding_view():
    return jsonify({"module": "onboarding", "status": "active", "description": "Onboarding submodule"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)