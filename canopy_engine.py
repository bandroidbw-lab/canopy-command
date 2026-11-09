from flask import Flask, render_template_string, request, redirect, url_for
import os
from supabase import create_client, Client

app = Flask(__name__)

# Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Shared Navigation Header Layout
NAV_BAR = """
<nav style="background: #1e1e1e; padding: 10px; margin-bottom: 20px; border-bottom: 2px solid #00ff66;">
    <a href="/" style="color: #00ff66; margin-right: 15px; text-decoration: none; font-weight: bold;">[D1: Foundation]</a>
    <a href="/leads" style="color: #00ff66; margin-right: 15px; text-decoration: none; font-weight: bold;">[D2: Lead Search]</a>
    <a href="/dispatch" style="color: #00ff66; margin-right: 15px; text-decoration: none; font-weight: bold;">[D3: Dispatch]</a>
    <a href="/callbacks" style="color: #00ff66; margin-right: 15px; text-decoration: none; font-weight: bold;">[D4: Callbacks]</a>
    <a href="/hazards" style="color: #00ff66; margin-right: 15px; text-decoration: none; font-weight: bold;">[D5: Spatial Hazards]</a>
    <a href="/estimator" style="color: #00ff66; text-decoration: none; font-weight: bold;">[D6: Estimator / Sold]</a>
</nav>
"""

BASE_STYLE = """
<style>
    body { font-family: monospace; background: #121212; color: #00ff66; padding: 20px; margin: 0; }
    h1, h2 { color: #fff; border-bottom: 1px solid #333; padding-bottom: 8px; }
    .card { background: #1e1e1e; border: 1px solid #333; padding: 15px; margin-bottom: 15px; border-radius: 5px; }
    .lead-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; margin-top: 15px; }
    .lead-card { background: #1a1a1a; border: 1px solid #00ff66; border-radius: 6px; overflow: hidden; display: flex; flex-direction: column; }
    .lead-img { width: 100%; height: 180px; object-fit: cover; background: #222; border-bottom: 1px solid #333; }
    .lead-content { padding: 15px; flex-grow: 1; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; background: #181818; }
    th, td { border: 1px solid #333; padding: 10px; text-align: left; color: #ddd; }
    th { background: #222; color: #00ff66; }
    .btn { background: #00ff66; color: #121212; padding: 8px 12px; border: none; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; }
    .btn-sold { background: #ff3333; color: #fff; }
    .badge { background: #333; color: #ffaa00; padding: 3px 6px; font-size: 0.8em; border-radius: 3px; }
    .search-bar { background: #181818; border: 1px solid #00ff66; padding: 10px; width: 100%; color: #fff; font-family: monospace; margin-bottom: 15px; box-sizing: border-box; }
</style>
"""

@app.route("/")
def d1_foundation():
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D1 Foundation & System Status</h1>
    <div class="card">
        <h3>Core Engine: ONLINE</h3>
        <p>Supabase Endpoint: Active</p>
        <p>Subscription Status: <span class="badge">TRIAL / MOCK MODE ACTIVE</span></p>
        <p>Operational Mode: Off-Grid Resilient / Starlink Ready</p>
    </div>
    """)

@app.route("/leads")
def d2_leads():
    search_query = request.args.get("q", "").lower()
    
    # Comprehensive mock lead dataset with front-facing property image placeholders
    all_leads = [
        {
            "id": 101, 
            "name": "Valley Solar & Prep LLC", 
            "parcel": "70226200 (Unit G-2)", 
            "phone": "(719) 555-0142", 
            "status": "Pending Opt-in", 
            "image": "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id": 102, 
            "name": "Blanca Off-Grid Builders", 
            "parcel": "4962 Stoner Road", 
            "phone": "(719) 555-0189", 
            "status": "Callback Due", 
            "image": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=600&auto=format&fit=crop&q=80"
        },
        {
            "id": 103, 
            "name": "San Luis Trenching Services", 
            "parcel": "Costilla Sector 4", 
            "phone": "(719) 555-0233", 
            "status": "Estimate Sent", 
            "image": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&auto=format&fit=crop&q=80"
        }
    ]

    if search_query:
        leads = [l for l in all_leads if search_query in l["name"].lower() or search_query in l["parcel"].lower() or search_query in l["phone"]]
    else:
        leads = all_leads
    
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D2 B2B Lead Search & Visual Cards <span class="badge">Mock / Trial Mode</span></h1>
    <div class="card">
        <form method="GET" action="/leads">
            <input type="text" name="q" class="search-bar" value="{{ query }}" placeholder="Search leads by company, parcel, or phone...">
            <button type="submit" class="btn">Filter Leads</button>
            <a href="/leads" class="btn" style="background:#333; color:#00ff66; margin-left:10px;">Reset</a>
        </form>
    </div>

    <div class="lead-grid">
        {% for l in leads %}
        <div class="lead-card">
            <img src="{{ l.image }}" alt="Property Front View" class="lead-img">
            <div class="lead-content">
                <h3 style="margin-top:0; color:#fff;">{{ l.name }}</h3>
                <p><strong>Parcel:</strong> {{ l.parcel }}</p>
                <p><strong>Phone:</strong> {{ l.phone }}</p>
                <p><strong>Status:</strong> <span class="badge">{{ l.status }}</span></p>
                <a href="/estimator?client={{ l.name }}" class="btn" style="margin-top:10px; width:100%; text-align:center; box-sizing:border-box;">Load into Estimator</a>
            </div>
        </div>
        {% endfor %}
    </div>
    """, leads=leads, query=search_query)

@app.route("/dispatch")
def d3_dispatch():
    mock_dispatches = [
        {"unit": "Unit 1 - Solar Crew", "location": "Stoner Rd Parcel (Blanca)", "task": "24V Array Mount & Wiring", "status": "Standby / Trial Active"},
        {"unit": "Unit 2 - Trenching & Site Prep", "location": "Costilla Unit G-2", "task": "Cistern & Septic Pad Grading", "status": "En Route"}
    ]
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D3 Field Dispatch Queue <span class="badge">Mock / Trial Mode</span></h1>
    <div class="card">
        <h3>Active Field Crews & Routes</h3>
        <table>
            <tr><th>Unit</th><th>Location</th><th>Assigned Task</th><th>Status</th></tr>
            {% for d in mock_dispatches %}
            <tr><td>{{ d.unit }}</td><td>{{ d.location }}</td><td>{{ d.task }}</td><td>{{ d.status }}</td></tr>
            {% endfor %}
        </table>
    </div>
    """, mock_dispatches=mock_dispatches)

@app.route("/callbacks", methods=["GET", "POST"])
def d4_callbacks():
    filter_type = request.args.get("session", "morning")
    mock_callbacks = [
        {"client": "Alamosa Supply Co.", "phone": "(719) 555-4921", "contact": "2026-11-02 09:00", "action": "Morning Scrubber Check"},
        {"client": "Costilla Excavation", "phone": "(719) 555-8830", "contact": "2026-11-02 14:30", "action": "Afternoon Follow-up"}
    ]
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D4 Callback Scrubber</h1>
    <div class="card">
        <a href="/callbacks?session=morning" class="btn">Morning Callbacks</a>
        <a href="/callbacks?session=afternoon" class="btn">Afternoon Callbacks</a>
        <h3>Current Session: {{ session | upper }} <span class="badge">Mock Data</span></h3>
        <table>
            <tr><th>Client</th><th>Phone</th><th>Last Contact</th><th>Action</th></tr>
            {% for c in mock_callbacks %}
            <tr><td>{{ c.client }}</td><td>{{ c.phone }}</td><td>{{ c.contact }}</td><td><a href="#" class="btn">{{ c.action }}</a></td></tr>
            {% endfor %}
        </table>
    </div>
    """, session=filter_type, mock_callbacks=mock_callbacks)

@app.route("/hazards")
def d5_hazards():
    mock_hazards = [
        {"parcel": "70226200 (Unit G-2)", "road": "Stoner Rd", "hazard": "High Desert Washout / Culvert Needed", "status": "Audited (Trial)"},
        {"parcel": "4962 Stoner Road (Blanca)", "road": "County Road 12", "hazard": "Sandy Approach / 4WD Recommended", "status": "Audited (Trial)"}
    ]
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D5 Spatial Hazard & Parcel Audit View <span class="badge">Mock / Trial Mode</span></h1>
    <div class="card">
        <h3>Costilla County / Local Parcel Overpass Data</h3>
        <table>
            <tr><th>Parcel ID</th><th>Access Road</th><th>Terrain Hazard</th><th>Status</th></tr>
            {% for h in mock_hazards %}
            <tr><td>{{ h.parcel }}</td><td>{{ h.road }}</td><td>{{ h.hazard }}</td><td>{{ h.status }}</td></tr>
            {% endfor %}
        </table>
    </div>
    """, mock_hazards=mock_hazards)

@app.route("/estimator", methods=["GET", "POST"])
def d6_estimator():
    msg = ""
    default_client = request.args.get("client", "")
    if request.method == "POST":
        client_name = request.form.get("client_name")
        msg = f"Job for {client_name} marked as SOLD & Dispatched (Trial Mode)!"
    
    return render_template_string(BASE_STYLE + NAV_BAR + """
    <h1>D6 Estimator & Instant 'Sold' Action</h1>
    <div class="card">
        {% if msg %}<p style="color: #00ff66; font-weight: bold;">{{ msg }}</p>{% endif %}
        <form method="POST">
            <label>Client Name / Parcel:</label><br><br>
            <input type="text" name="client_name" value="{{ default_client }}" style="padding: 8px; width: 300px; background: #222; color: #fff; border: 1px solid #444;" required><br><br>
            <button type="submit" class="btn btn-sold">INSTANT 'SOLD' & DISPATCH</button>
        </form>
    </div>
    """, msg=msg, default_client=default_client)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
