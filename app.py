from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='.')

@app.route('/')
def index():
    return "Canopy Command Master Root - Active"

# --- D4 Outreach & Dialer Demo Routes ---
@app.route('/d4/dialer/anchor-address-demo')
def d4_anchor_address_demo():
    return render_template('d4phone/dialer/d2admindemo/anchoraddressdemo/index.html')

@app.route('/d4/dialer/lead-queue-demo')
def d4_lead_queue_demo():
    return render_template('d4phone/dialer/d2admindemo/leadqueuedemo/index.html')

@app.route('/d4/dialer/text-demo')
def d4_text_demo():
    return render_template('d4phone/dialer/d2admindemo/textdemo/index.html')

@app.route('/d4/dialer/zip-subscriptions-demo')
def d4_zip_subscriptions_demo():
    return render_template('d4phone/dialer/d2admindemo/zipsubscriptionsdemo/index.html')

# --- D6 Admin & Member Routes ---
@app.route('/d6')
def d6_admin_root():
    return jsonify({
        "service": "canopy-command-d6admin",
        "status": "governance_active",
        "branch": "Admin Control & Onboarding"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)