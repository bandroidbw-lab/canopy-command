import os
from flask import Flask
from supabase import create_client, Client

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

@app.route('/')
def home():
    status = "Connected to Supabase" if supabase else "Missing Supabase Credentials"
    return f"CanopyCommand Cloud Engine Live & Operational | Status: {status}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
