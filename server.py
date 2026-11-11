from flask import Flask, render_template, jsonify, request
import os
import json
from datetime import datetime
import threading
import time

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
        self.current_index = 0
        self.queue = [
            {"phone": "704-555-0101", "name": "Piedmont Tree Experts", "status": "pending"},
            {"phone": "704-555-0102", "name": "Carolina Canopy Care", "status": "pending"},
            {"phone": "704-555-0103", "name": "Apex Arborists", "status": "pending"},
            {"phone": "864-555-0104", "name": "Upstate Timber Service", "status": "pending"},
            {"phone": "540-555-0105", "name": "Blue Ridge Cutters", "status": "pending"}
        ]
        self.prime_callbacks = []
        self.active_list_name = "default_session"
        self.active_call = None
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

    def save_session(self):
        os.makedirs("saved_lists", exist_ok=True)
        filename = f"saved_lists/session_{self.active_list_name}.json"
        data = {
            "active_corridor": self.active_corridor,
            "current_index": self.current_index,
            "status": self.status,
            "queue": self.queue,
            "prime_callbacks": self.prime_callbacks,
            "metrics": self.metrics
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filename

    def load_session(self, list_name):
        filename = f"saved_lists/session_{list_name}.json"
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.active_list_name = list_name
                self.active_corridor = data.get("active_corridor", self.active_corridor)
                self.current_index = data.get("current_index", 0)
                self.status = data.get("status", "IDLE")
                self.queue = data.get("queue", [])
                self.prime_callbacks = data.get("prime_callbacks", [])
                self.metrics = data.get("metrics", self.metrics)
                return True
        return False

    def process_call_result(self, contact, result_type, duration=0):
        self.metrics["total_tried"] += 1
        self.metrics["call_durations"].append({
            "phone": contact.get("phone"),
            "name": contact.get("name", "Contractor"),
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
            if not any(c['phone'] == contact.get('phone') for c in self.prime_callbacks):
                self.prime_callbacks.append({
                    "phone": contact.get("phone"),
                    "name": contact.get("name", "Contractor"),
                    "duration": duration
                })

        self.save_session()

    def get_scoreboard(self):
        # Sort prime callbacks by duration descending (longest on phone first)
        sorted_callbacks = sorted(self.prime_callbacks, key=lambda x: x.get("duration", 0), reverse=True)
        sorted_durations = sorted(self.metrics["call_durations"], key=lambda x: x["duration"], reverse=True)
        saved_files = []
        if os.path.exists("saved_lists"):
            saved_files = [f.replace("session_", "").replace(".json", "") for f in os.listdir("saved_lists") if f.startswith("session_")]

        return {
            "status": self.status,
            "target": self.target_count,
            "collected": len(self.prime_callbacks),
            "active_corridor": self.active_corridor,
            "current_index": self.current_index,
            "active_list_name": self.active_list_name,
            "saved_lists": saved_files,
            "queue": self.queue,
            "active_call": self.active_call,
            "prime_callbacks": sorted_callbacks,
            "script_config": self.script_config,
            "metrics": self.metrics,
            "duration_graph": sorted_durations
        }

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'd4phone', 'templates'))
app = Flask(__name__, template_folder=template_dir)
engine = BroadcasterEngine(target_count=50)

# Autonomous Autodialer Background Worker Thread
def autodialer_worker():
    while True:
        if engine.status == "RUNNING":
            if engine.current_index < len(engine.queue):
                contact = engine.queue[engine.current_index]
                engine.active_call = contact
                
                # Simulate live autonomous dial call duration (e.g. 15-45 seconds)
                time.sleep(4) 
                
                # Simulate result classification (In-service primary pickup)
                engine.process_call_result(contact, "in_service", duration=42)
                engine.current_index += 1
            else:
                engine.status = "COMPLETED"
                engine.active_call = None
                engine.save_session()
        else:
            engine.active_call = None
        time.sleep(1)

threading.Thread(target=autodialer_worker, daemon=True).start()

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
        engine.save_session()
    elif action == "stop":
        engine.status = "IDLE"
        engine.save_session()
    return jsonify({"status": engine.status})

@app.route("/api/broadcaster/market", methods=["POST"])
def update_market():
    data = request.json or {}
    market_key = data.get("market_key")
    success = engine.set_market(market_key)
    return jsonify({"success": success, "active_corridor": engine.active_corridor, "target": engine.target_count})

@app.route("/api/broadcaster/load-list", methods=["POST"])
def load_list():
    data = request.json or {}
    list_name = data.get("list_name")
    success = engine.load_session(list_name)
    return jsonify({"success": success, "scoreboard": engine.get_scoreboard()})

@app.route("/api/broadcaster/dial-manual", methods=["POST"])
def dial_manual():
    data = request.json or {}
    phone = data.get("phone")
    name = data.get("name", "Manual Target")
    # Instantly set active call for manual override dialing
    engine.active_call = {"phone": phone, "name": name, "status": "manual_dialing"}
    engine.process_call_result({"phone": phone, "name": name}, "in_service", duration=55)
    return jsonify({"success": True, "scoreboard": engine.get_scoreboard()})

@app.route("/health")
def health():
    return jsonify({"service": "canopy-command-d4-dialer", "status": "operational"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)