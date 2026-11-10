import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def d2_demo_home():
    return jsonify({
        "service": "canopy-command-d2-demo",
        "status": "operational",
        "description": "Public demo board server."
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)