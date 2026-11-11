import os
import json
from datetime import datetime

class BroadcasterEngine:
    def __init__(self, target_count=50):
        self.target_count = target_count
        self.active_corridor = "Lower States High-Density Canopy Corridor"
        self.status = "IDLE" # IDLE, RUNNING, PAUSED, COMPLETED
        self.queue = []
        self.prime_callbacks = []
        self.metrics = {
            "total_tried": 0,
            "in_service": 0,
            "faxes": 0,
            "modems": 0,
            "out_of_service": 0,
            "call_durations": []
        }

    def load_prospects(self, prospects):
        """Load prospects sorted by longest-dialed-out priority."""
        # Sort by dial duration / priority descending
        self.queue = sorted(prospects, key=lambda x: x.get("dial_duration", 0), reverse=True)

    def process_call_result(self, contact, result_type, duration=0):
        """
        result_type: 'in_service', 'fax', 'modem', 'out_of_service'
        """
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

        # Check completion quota
        if len(self.prime_callbacks) >= self.target_count:
            self.status = "COMPLETED"
            self.save_completed_list()

    def save_completed_list(self):
        """Save completed 50-prime list timestamped by creation date."""
        os.makedirs("d4phone/saved_lists", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
        filename = f"d4phone/saved_lists/broadcast_list_{date_str}.json"
        
        data = {
            "created_at": datetime.now().isoformat(),
            "corridor": self.active_corridor,
            "total_prime": len(self.prime_callbacks),
            "metrics": self.metrics,
            "contacts": self.prime_callbacks
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        
        return filename

    def get_scoreboard(self):
        # Sort call durations descending for the scoreboard graph view
        sorted_durations = sorted(self.metrics["call_durations"], key=lambda x: x["duration"], reverse=True)
        return {
            "status": self.status,
            "target": self.target_count,
            "collected": len(self.prime_callbacks),
            "metrics": self.metrics,
            "duration_graph": sorted_durations
        }