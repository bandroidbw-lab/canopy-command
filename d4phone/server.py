from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

@app.route("/")
@app.route("/dialer")
def d4_dialer():
    return render_template("d4_dialer.html")

@app.route("/health")
def health():
    return jsonify({"service": "canopy-command-d4-dialer", "status": "operational"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)