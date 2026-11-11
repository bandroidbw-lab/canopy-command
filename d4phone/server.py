from flask import Flask, render_template, jsonify, request
from d4phone.broadcaster import BroadcasterEngine

app = Flask(__name__)
engine = BroadcasterEngine(target_count=50)

@app.route("/")
@app.route("/dialer")
def d4_dialer():
return render_template("d4_dialer.html")

@app.route("/api/broadcaster/status", methods=["GET"])
def get_broadcaster_status():
return jsonify(engine.get_scoreboard())

@app.route("/api/broadcaster/control", methods=["POST"])
def control_broadcaster():
data = request.json or {}
action = data.get("action")

if action == "start":
    engine.status = "RUNNING"
elif action == "pause":
    engine.status = "PAUSED"
elif action == "stop":
    engine.status = "IDLE"
    
return jsonify({"status": engine.status})

@app.route("/api/broadcaster/feed", methods=["POST"])
def feed_call_result():
data = request.json or {}
contact = data.get("contact", {})
result_type = data.get("result_type", "in_service")
duration = data.get("duration", 30)

engine.process_call_result(contact, result_type, duration)
return jsonify(engine.get_scoreboard())

@app.route("/health")
def health():
return jsonify({"service": "canopy-command-d4-dialer", "status": "operational"})

if __name__ == "__main__":
app.run(host="0.0.0.0", port=5000)
