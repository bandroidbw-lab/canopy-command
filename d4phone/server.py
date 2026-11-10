import os
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def d4_home():
    return jsonify({
        "service": "canopy-command-d4-dialer",
        "status": "operational",
        "description": "High-density commercial cold calling & broadcasting console."
    }), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)