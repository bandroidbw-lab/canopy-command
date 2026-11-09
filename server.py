import os
from flask import Flask

# Import your Flask app instance from app.py, with a safe fallback
try:
    from app import app
except ImportError:
    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Canopy Command System Online"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)