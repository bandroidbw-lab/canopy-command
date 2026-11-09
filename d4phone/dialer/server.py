from flask import Flask, render_template

app = Flask(__name__, template_folder='../../templates') # Point to shared root templates

@app.route('/')
def dashboard():
    return render_template('base_dashboard.html', 
                           service_name="D4 Dialer / D6 Admin Hub", 
                           modules=["anchoraddress", "d2member", "onboarding", "reports", "searchhazards"])