from flask import Flask, render_template, jsonify, request
import os
import json
from datetime import datetime

MARKET_CORRIDORS = {
    "NC-01": {"name": "North Carolina Piedmont Corridor", "target_count": 50, "prefix": "704"},
    "SC-02": {"name": "Upstate South Carolina Canopy", "target_count": 50, "prefix": "864"},
    "VA-03": {"name": "Virginia Blue Ridge Foothills", "target_count": 50, "prefix": "540"},
    "GA-04": {"name": "North Georgia Timber Belt", "target_count": 50, "prefix": "706"}
}

class BroadcasterEngine:
    def __init__(self, target_count=50):
        self.target_count = target_count
        self.active_corridor = "North Carolina Piedmont Corridor"
        self.status = "IDLE"
        self.queue = []
        self.prime_callbacks = []
        self.script_config = {
            "persona": "Energetic Tree Care Specialist",
            "voice_model": "en-US-Neural2-F (High Energy & Natural)",
            "script_template": "Hello {contractor_name}, this is Canopy Command. We noticed your tree service crew operating in the {corridor} corridor and wanted to secure your spot for our upcoming high-density prime contractor quota."
        }
        self.metrics = {
            "total_tried": 0,
            "in_service": 0,
            "faxes": 0,
            "modems": 0,
            "out_of_service": 0,
            "call_durations": []
        }

    def set_market(self, market_key):
        if market_key in MARKET_CORRIDORS:
            market = MARKET_CORRIDORS[market_key]
            self.active_corridor = market["name"]
            self.target_count = market["target_count"]
            return True
        return False

    def update_script(self, new_template, persona, voice_model):
        self.script_config["script_template"] = new_template
        self.script_config["persona"] = persona
        self.script_config["voice_model"] = voice_model
        return self.script_config

    def process_call_result(self, contact, result_type, duration=0):
        self.metrics["total_tried"] += 1
        self.metrics["call_durations"].append({
            "phone": contact.get("phone"),
            "duration": duration
        })

        if result_type == "fax":
            self.metrics["faxes"] += 1
        elif result_type == "modem":
            self.metrics["modems"] += 1
        elif result_type == "out_of_service":
            self.metrics["out_of_service"] += 1
        elif result_type == "in_service":
            self.metrics["in_service"] += 1
            if len(self.prime_callbacks) < self.target_count:
                self.prime_callbacks.append(contact)

        if len(self.prime_callbacks) >= self.target_count:
            self.status = "COMPLETED"
            self.save_completed_list()

    def save_completed_list(self):
        os.makedirs("saved_lists", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"saved_lists/broadcast_list_{date_str}.json"
        data = {
            "created_at": datetime.now().isoformat(),
            "corridor": self.active_corridor,
            "total_prime": len(self.prime_callbacks),
            "script_used": self.script_config,
            "metrics": self.metrics,
            "contacts": self.prime_callbacks
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filename

    def get_scoreboard(self):
        sorted_durations = sorted(self.metrics["call_durations"], key=lambda x: x["duration"], reverse=True)
        return {
            "status": self.status,
            "target": self.target_count,
            "collected": len(self.prime_callbacks),
            "active_corridor": self.active_corridor,
            "script_config": self.script_config,
            "metrics": self.metrics,
            "duration_graph": sorted_durations
        }

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'd4phone', 'templates'))
app = Flask(__name__, template_folder=template_dir)
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

@app.route("/api/broadcaster/market", methods=["POST"])
def update_market():
    data = request.json or {}
    market_key = data.get("market_key")
    success = engine.set_market(market_key)
    return jsonify({"success": success, "active_corridor": engine.active_corridor, "target": engine.target_count})

@app.route("/api/broadcaster/script", methods=["POST"])
def update_broadcaster_script():
    data = request.json or {}
    template = data.get("script_template")
    persona = data.get("persona")
    voice_model = data.get("voice_model")
    updated = engine.update_script(template, persona, voice_model)
    return jsonify({"success": True, "script_config": updated})

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