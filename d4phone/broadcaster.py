import os
import json
from datetime import datetime

class BroadcasterEngine:
    def __init__(self, target_count=50):
        self.target_count = target_count
        self.active_corridor = "Lower States High-Density Canopy Corridor"
        self.status = "IDLE"
        self.queue = []
        self.prime_callbacks = []
        
        # AI Script & Voice Configuration
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
        os.makedirs("d4phone/saved_lists", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"d4phone/saved_lists/broadcast_list_{date_str}.json"
        
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
            "script_config": self.script_config,
            "metrics": self.metrics,
            "duration_graph": sorted_durations
        }