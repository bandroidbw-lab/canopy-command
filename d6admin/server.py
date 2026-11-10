import os
from flask import Flask, render_template

# Tell Flask explicitly where to find the templates folder inside d6admin/
app = Flask(__name__, template_folder='templates')

@app.route('/', methods=['GET'])
def d6_home():
    # Renders d6admin/templates/index.html
    return render_template('index.html')

@app.route('/d6/reports', methods=['GET'])
def d6_reports():
    # Renders d6admin/templates/reports.html
    return render_template('reports.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)