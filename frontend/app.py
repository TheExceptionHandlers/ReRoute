import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image
import io
import pandas as pd
import numpy as np
from streamlit_geolocation import streamlit_geolocation

# --- ROBUST STATE MANAGEMENT ---
if "payload" not in st.session_state: st.session_state.payload = None
if "loc_lat" not in st.session_state: st.session_state.loc_lat = 12.9352
if "loc_lon" not in st.session_state: st.session_state.loc_lon = 77.6245
if "loc_address" not in st.session_state: st.session_state.loc_address = "Koramangala 4th Block, Bengaluru, India"
if "location_confirmed" not in st.session_state: st.session_state.location_confirmed = True
if "uploaded_bytes" not in st.session_state: st.session_state.uploaded_bytes = None
if "uploaded_name" not in st.session_state: st.session_state.uploaded_name = None
if "uploaded_type" not in st.session_state: st.session_state.uploaded_type = None
if "receipt_verified" not in st.session_state: st.session_state.receipt_verified = None
if "last_clicked_lat" not in st.session_state: st.session_state.last_clicked_lat = None
if "last_clicked_lon" not in st.session_state: st.session_state.last_clicked_lon = None
if "selected_workflow" not in st.session_state: st.session_state.selected_workflow = "Option A: Self Drop-off (Get Instant Refund)"
if "selected_product" not in st.session_state: st.session_state.selected_product = "Alpine Trail Shell Jacket"
if "retail_price" not in st.session_state: st.session_state.retail_price = 8500.00
if "service_booked" not in st.session_state: st.session_state.service_booked = False

# Mock Artisan Job Queue state for the demo
if "artisan_jobs" not in st.session_state:
    st.session_state.artisan_jobs = [
        {"id": "JOB-9021", "item": "Alpine Trail Shell Jacket", "defect": "Stuck/Misaligned Zipper", "eta": "24h", "bounty": "₹450.00", "status": "Pending Pickup / Drop-off"},
        {"id": "JOB-9022", "item": "Vanguard All-Terrain Boots", "defect": "Sole Separation", "eta": "48h", "bounty": "₹600.00", "status": "In Repair"},
        {"id": "JOB-9023", "item": "Merino Wool Commuter Sweater", "defect": "Sleeve Tear", "eta": "12h", "bounty": "₹300.00", "status": "Completed & Escrow Released"}
    ]

# Mock Delivery Tasks for the Courier Portal
if "delivery_tasks" not in st.session_state:
    st.session_state.delivery_tasks = [
        {
            "id": "DEL-501", 
            "customer_name": "Sai Dasaradharam G.", 
            "item": "Alpine Trail Shell Jacket", 
            "pickup_address": "Koramangala 4th Block, Bengaluru, India", 
            "handoff_address": "Stitch & Save Atelier, Koramangala 4th Block, Bengaluru", 
            "status": "Assigned - En Route to Pickup"
        }
    ]

# --- GEOCODING HELPER ---
def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        res = requests.get(url, headers={'User-Agent': 'ReRoute/1.0'}, timeout=5)
        if res.status_code == 200: return res.json().get('display_name', 'Address not found')
    except Exception: pass
    return f"Lat: {lat:.5f}, Lon: {lon:.5f}"

# --- PAGE UI & STYLING ---
st.set_page_config(page_title="ReRoute | Smart Returns", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
    
    .stApp { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0 !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 0.75rem 1.5rem !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }

    .metric-wrapper {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
        border: none;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 20px -5px rgba(49, 46, 129, 0.3);
    }
    .metric-label { font-size: 0.8rem; text-transform: uppercase; color: #c7d2fe; font-weight: 700; letter-spacing: 0.05em; margin-bottom: 8px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 0; }
    .metric-value.positive { color: #34d399; }

    .status-banner {
        font-family: 'JetBrains Mono', monospace;
        padding: 16px 24px;
        border-radius: 12px;
        font-weight: 700;
        margin-bottom: 24px;
        font-size: 0.95rem;
        display: flex;
        gap: 12px;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .status-active { background: linear-gradient(135deg, #065f46 0%, #047857 100%); color: #ecfdf5; border: none; }

    h1 { color: #1e1b4b; font-weight: 800 !important; letter-spacing: -0.025em; }
    h5 { color: #312e81; font-weight: 700 !important; }
</style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, positive=False):
    return f'<div class="metric-wrapper"><div class="metric-label">{label}</div><p class="metric-value{" positive" if positive else ""}">{value}</p></div>'

# --- TOP HEADER BAR WITH NAVIGATION DROPDOWN ---
col_title, col_nav = st.columns([2.2, 1.8], vertical_alignment="bottom")
with col_title:
    st.title("ReRoute")
    st.markdown("<p style='color: #64748b; font-size: 1rem; margin-top: -10px; margin-bottom: 0rem;'>Autonomous Multi-Agent Reverse Logistics Ecosystem</p>", unsafe_allow_html=True)
with col_nav:
    app_role = st.selectbox(
        "Navigation View", 
        ["🛒 Customer Portal", "🛠️ Artisan Partner Portal", "🚚 Delivery Partner Portal", "📈 Enterprise Mission Control"], 
        label_visibility="collapsed", 
        key="top_nav_role"
    )

st.divider()

# --- VIEW 1: ARTISAN PARTNER PORTAL ---
if app_role == "🛠️ Artisan Partner Portal":
    st.markdown("### 🧵 Service Provider Command Center: *Stitch & Save Atelier (Koramangala)*")
    st.info("This interface simulates the lightweight web portal provided to local micro-fulfillment artisans to manage incoming AI-routed repair tasks and escrow payouts.")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    col_a1.metric("Pending Incoming Jobs", "2 Items", "+1 today")
    col_a2.metric("Completed This Week", "14 Items", "99.2% SLA")
    col_a3.metric("Escrow Balance Ready", "₹1,350.00", "Auto-Payout Fri")

    st.divider()
    st.markdown("#### 📥 Incoming Jobs Feed & Task Queue")
    
    for idx, job in enumerate(st.session_state.artisan_jobs):
        with st.container(border=True):
            cols = st.columns([2, 2, 1, 1.5])
            cols[0].markdown(f"**{job['item']}**\n\n*Defect:* {job['defect']}")
            cols[1].markdown(f"*Target ETA:* `{job['eta']}`\n\n*Bounty:* **{job['bounty']}**")
            cols[2].markdown(f"Status:\n`{job['status']}`")
            
            with cols[3]:
                status = job["status"]
                if status == "Pending Pickup / Drop-off":
                    if st.button("📥 Accept & Start Repair", key=f"action_job_{idx}", type="secondary"):
                        job["status"] = "In Repair"
                        st.rerun()
                elif status == "In Repair":
                    if st.button("🛠️ Mark Repair Complete", key=f"action_job_{idx}", type="primary"):
                        job["status"] = "Completed & Escrow Released"
                        st.success("Escrow bounty released to artisan account!")
                        st.rerun()
                else:
                    st.success("✅ Payout Released")

    st.divider()
    st.markdown("#### 💳 Weekly Escrow & Payout Ledger")
    ledger_data = pd.DataFrame([
        {"Tx ID": "TXN-8810", "Item": "Alpine Trail Jacket", "Bounty": "₹450.00", "Status": "Escrow Released", "Date": "2026-10-17"},
        {"Tx ID": "TXN-8811", "Item": "Leather Boots Sole", "Bounty": "₹600.00", "Status": "Escrow Released", "Date": "2026-10-18"},
        {"Tx ID": "TXN-8812", "Item": "Commuter Sweater", "Bounty": "₹300.00", "Status": "Pending Verification", "Date": "2026-10-18"}
    ])
    st.dataframe(ledger_data, use_container_width=True)

# --- VIEW 2: DELIVERY PARTNER PORTAL ---
elif app_role == "🚚 Delivery Partner Portal":
    st.markdown("### 🛵 Courier & Logistics Dispatch Hub")
    st.info("Active field assignments for local delivery partners managing Option B pickups and artisan handoffs.")

    for idx, task in enumerate(st.session_state.delivery_tasks):
        with st.container(border=True):
            st.markdown(f"#### Task ID: `{task['id']}` — {task['item']}")
            st.write(f"**Customer Name:** {task['customer_name']}")
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"📍 **Pickup Location (Customer):**\n`{task['pickup_address']}`")
            with col_d2:
                st.markdown(f"🏁 **Handoff Location (Artisan Shop):**\n`{task['handoff_address']}`")
            
            st.divider()
            st.markdown(f"**Current Status:** `{task['status']}`")
            
            status = task["status"]
            if status == "Assigned - En Route to Pickup":
                if st.button("📦 Mark as Picked Up from Customer", key=f"pick_{idx}", type="primary"):
                    task["status"] = "Picked Up - In Transit to Artisan"
                    st.rerun()
            elif status == "Picked Up - In Transit to Artisan":
                if st.button("🏁 Complete Handoff to Artisan Shop", key=f"hand_{idx}", type="primary"):
                    task["status"] = "Delivered & Handed Over to Artisan"
                    st.success("Delivery completed successfully!")
                    st.rerun()
            else:
                st.success("✅ Delivery & Handoff Completed")

# --- VIEW 3: ENTERPRISE MISSION CONTROL ---
# --- VIEW: ENTERPRISE MISSION CONTROL & TREASURY ---
elif app_role == "📈 Enterprise Mission Control":
    st.markdown("### 📈 Enterprise Executive Command Center")
    st.markdown("<p style='color: #64748b;'>Real-time supply chain telemetry, ESG tracking, and escrow financial disbursement ledger.</p>", unsafe_allow_html=True)

    # Executive Metrics Row
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items Diverted Locally", "12,482", "+14%")
    m2.metric("Logistics Cost Saved", "₹48.5L", "+22%")
    m3.metric("Scope-3 CO₂ Prevented", "14.2 Tons", "+8%")
    m4.metric("Active Local Artisans", "843", "+42")
    
    st.divider()

    # Analytics Charts Row
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Daily Freight Avoidance Savings (₹)**")
        chart_data = pd.DataFrame(np.random.randn(30, 1) * 10000 + 150000, columns=["Savings"])
        st.line_chart(chart_data)
    with col_chart2:
        st.markdown("**Returns by Defect Category**")
        defect_data = pd.DataFrame({"Category": ["Zippers", "Tears/Seams", "Soles", "Electronics"], "Count": [4500, 3200, 2100, 2682]}).set_index("Category")
        st.bar_chart(defect_data)

    st.divider()

    # --- NEW: ENTERPRISE ESCROW & PAYMENT DISBURSEMENT GATEWAY ---
    st.markdown("### 💳 Enterprise Treasury & Payment Release Ledger")
    st.info("Finance approval gateway for automated customer refunds (Fraud Guard verified) and artisan service bounty disbursements.")

    tab_escrow_cust, tab_escrow_art = st.tabs(["🛒 Customer Refund Approvals", "🛠️ Artisan Payout Disbursements"])

    with tab_escrow_cust:
        st.markdown("#### Pending Customer Reimbursements (Fraud Guard Verified)")
        cust_claims = pd.DataFrame([
            {"Claim ID": "CLM-301", "Customer": "Sai Dasaradharam G.", "Item": "Alpine Trail Jacket", "Est. Cost": "₹450.00", "Receipt Bill": "Verified (₹440.00)", "Status": "Pending Approval"},
            {"Claim ID": "CLM-302", "Customer": "Ananya Sharma", "Item": "Vanguard Boots", "Est. Cost": "₹600.00", "Receipt Bill": "Verified (₹590.00)", "Status": "Ready for Release"}
        ])
        
        for idx, row in cust_claims.iterrows():
            with st.container(border=True):
                c_cols = st.columns([2, 2, 1, 1.5])
                c_cols[0].markdown(f"**{row['Claim ID']}** — {row['Customer']}\n\n*Item:* {row['Item']}")
                c_cols[1].markdown(f"*Estimate:* {row['Est. Cost']}\n\n*Bill Upload:* `{row['Receipt Bill']}`")
                c_cols[2].markdown(f"Status:\n`{row['Status']}`")
                with c_cols[3]:
                    if st.button(f"💸 Release Refund", key=f"rel_cust_{idx}", type="primary"):
                        st.success(f"Successfully disbursed refund for {row['Claim ID']}!")
                        st.rerun()

    with tab_escrow_art:
        st.markdown("#### Artisan Repair Bounty Payouts (Milestone Completed)")
        art_claims = pd.DataFrame([
            {"Job ID": "JOB-9021", "Artisan Shop": "Stitch & Save Atelier", "Item": "Alpine Trail Jacket", "Bounty": "₹450.00", "Milestone": "Repair Completed"},
            {"Job ID": "JOB-9022", "Artisan Shop": "EcoSole Cobblers", "Item": "All-Terrain Boots", "Bounty": "₹600.00", "Milestone": "Ready for Pickup"}
        ])

        for idx, row in art_claims.iterrows():
            with st.container(border=True):
                a_cols = st.columns([2, 2, 1, 1.5])
                a_cols[0].markdown(f"**{row['Job ID']}** — {row['Artisan Shop']}\n\n*Item:* {row['Item']}")
                a_cols[1].markdown(f"*Bounty Amount:* **{row['Bounty']}**")
                a_cols[2].markdown(f"Milestone:\n`{row['Milestone']}`")
                with a_cols[3]:
                    if st.button(f"⚡ Release Payout", key=f"rel_art_{idx}", type="primary"):
                        st.success(f"Successfully released escrow bounty for {row['Job ID']}!")
                        st.rerun()
# --- VIEW 4: CUSTOMER PORTAL ---
else:
    is_active = st.session_state.payload is not None

    if not is_active:
        _, center_container, _ = st.columns([0.2, 1, 0.2])
        with center_container:
            with st.container(border=True):
                st.markdown("##### 📦 Step 1: Return Details")
                c1, c2 = st.columns(2)
                with c1:
                    product_options = {"Alpine Trail Shell Jacket": 8500.00, "Vanguard All-Terrain Boots": 12000.00, "Merino Wool Commuter Sweater": 4500.00}
                    selected_product = st.selectbox("Product Item", list(product_options.keys()), key="sel_prod")
                with c2:
                    retail_price = st.number_input("Retail Price (₹)", value=product_options[selected_product], format="%.2f", key="ret_price")
            
            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("##### 🚚 Step 2: Return Method")
                selected_workflow = st.radio(
                    "How would you like to return this?",
                    ["Option A: Self Drop-off (Get Instant Refund)", "Option B: Schedule a Pickup"],
                    key="sel_work"
                )
                st.session_state.selected_workflow = selected_workflow
                st.divider()
                st.markdown("##### 📍 Pin Your Location on Map")
                st.caption("Click anywhere on the map to select your pickup/drop-off point, or click 'Detect Current Location'.")
                
                gps_trigger = streamlit_geolocation()
                if gps_trigger and gps_trigger.get('latitude'):
                    g_lat = float(gps_trigger['latitude'])
                    g_lon = float(gps_trigger['longitude'])
                    if g_lat != st.session_state.loc_lat:
                        st.session_state.loc_lat = g_lat
                        st.session_state.loc_lon = g_lon
                        st.session_state.loc_address = reverse_geocode(g_lat, g_lon)
                        st.session_state.location_confirmed = True
                        st.rerun()

                try:
                    m_map = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                    folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Selected Location", icon=folium.Icon(color="red", icon="user")).add_to(m_map)
                    
                    m_data = st_folium(m_map, height=280, use_container_width=True, key="primary_map", returned_objects=["last_clicked"])
                    
                    if m_data and m_data.get("last_clicked"):
                        c_lat = m_data["last_clicked"]["lat"]
                        c_lon = m_data["last_clicked"]["lng"]
                        if c_lat != st.session_state.last_clicked_lat or c_lon != st.session_state.last_clicked_lon:
                            st.session_state.last_clicked_lat = c_lat
                            st.session_state.last_clicked_lon = c_lon
                            st.session_state.loc_lat = c_lat
                            st.session_state.loc_lon = c_lon
                            st.session_state.loc_address = reverse_geocode(c_lat, c_lon)
                            st.session_state.location_confirmed = True
                            st.rerun()
                except Exception:
                    st.caption("Map preview unavailable.")

                st.success(f"✅ Location Selected: {st.session_state.loc_address}")

            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("##### 📸 Step 3: Upload Item Photo")
                uploaded_file = st.file_uploader("Upload damage photo", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="dmg_upload")
                if uploaded_file:
                    st.session_state.uploaded_bytes = uploaded_file.getvalue()
                    st.session_state.uploaded_name = uploaded_file.name
                    st.session_state.uploaded_type = uploaded_file.type
                
                if st.session_state.uploaded_bytes:
                    st.image(Image.open(io.BytesIO(st.session_state.uploaded_bytes)), caption="Photo Uploaded Successfully", width=250)

            can_process = st.session_state.uploaded_bytes is not None
            if not can_process:
                st.warning("⚠️ Please upload a damage photo to proceed.")

            st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
            process_btn = st.button("⚡ Analyze Return & Find Local Repair", use_container_width=True, type="primary", disabled=not can_process, key="analyze_btn")

            if process_btn and st.session_state.uploaded_bytes:
                st.session_state.selected_product = selected_product
                st.session_state.retail_price = retail_price
                st.session_state.payload = None 
                st.session_state.receipt_verified = None
                backend_url = "http://127.0.0.1:8000/api/v1/intercept"
                with st.status("Analyzing photo and locating nearest verified repair partner...", expanded=True) as status:
                    file_bytes = st.session_state.uploaded_bytes
                    files = {"file": (st.session_state.uploaded_name, file_bytes, st.session_state.uploaded_type or "image/jpeg")}
                    data = {"product_name": selected_product, "retail_price": str(retail_price), "customer_lat": str(st.session_state.loc_lat), "customer_lon": str(st.session_state.loc_lon)}
                    try:
                        response = requests.post(backend_url, data=data, files=files, timeout=90)
                        if response.status_code == 200:
                            st.session_state.payload = response.json()
                            status.update(label="Analysis Complete", state="complete")
                            st.rerun()
                        else:
                            status.update(label="Connection Failed", state="error")
                            st.error(f"Backend Error [{response.status_code}]: {response.text}")
                    except Exception as e:
                        status.update(label="Network Timeout", state="error")
                        st.error(f"Could not reach backend server: {str(e)}")
    else:
        col_left, col_right = st.columns([1, 1.4], gap="large")
        
        with col_left:
            st.markdown("##### 📦 Locked Return Details")
            with st.container(border=True):
                st.write(f"**Address:** {st.session_state.loc_address}")
                st.write(f"**Method:** {st.session_state.selected_workflow}")
            if st.button("🔄 Start New Return", use_container_width=True):
                st.session_state.payload = None
                st.session_state.uploaded_bytes = None
                st.session_state.service_booked = False
                st.rerun()

        with col_right:
            payload = st.session_state.payload
            diag = payload.get("diagnosis", {})
            is_repairable = diag.get("is_repairable", True)
            workflow = st.session_state.selected_workflow
            item_name = st.session_state.get("selected_product", "Alpine Trail Shell Jacket")

            if not is_repairable:
                st.markdown('<div class="status-banner" style="background-color: #450a0a; color: #fca5a5; border: 1px solid #b91c1c;">● SYSTEM STATUS: TOTAL LOSS - ROUTED TO SALVAGE</div>', unsafe_allow_html=True)
                st.error(f"**AI Diagnosis (Unrepairable):** {diag.get('defect_summary', 'Item is damaged beyond functional restoration limits.')}")
            else:
                if "Option A" in workflow:
                    st.markdown('<div class="status-banner" style="background-color: #0f2830; color: #38bdf8; border: 1px solid #0284c7;">⚡ WORKFLOW ACTIVE: SELF DROP-OFF & INSTANT REIMBURSEMENT</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-banner" style="background-color: #3b1f0c; color: #fb923c; border: 1px solid #f97316;">🚚 WORKFLOW ACTIVE: MANAGED COURIER PICKUP & RECOMMERCE</div>', unsafe_allow_html=True)

                raw_arb = payload.get("arbitrage", {})
                arb = raw_arb.get("match_artisan_and_arbitrage_response", raw_arb)
                artisan = arb.get("artisan_matched", {})
                
                with st.container(border=True):
                    st.markdown("##### 🗺️ Local Repair Partner Details")
                    if artisan and artisan.get("latitude") and artisan.get("longitude"):
                        st.info(f"**Matched Shop:** {artisan.get('name', 'Artisan Partner')} | **Estimated Turnaround:** {diag.get('repair_turnaround_hours', 24)}h\n\n**Address:** {artisan.get('address', 'N/A')}\n\n**AI Diagnosis:** {str(diag.get('defect_type', 'Unknown')).replace('_', ' ').title()} - {diag.get('defect_summary', '')}")
                        try:
                            m = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                            folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Customer Location", icon=folium.Icon(color="red", icon="user")).add_to(m)
                            art_lat, art_lon = float(artisan["latitude"]), float(artisan["longitude"])
                            folium.Marker([art_lat, art_lon], popup=f"<b>{artisan.get('name')}</b>", icon=folium.Icon(color="green", icon="wrench", prefix="fa")).add_to(m)
                            folium.PolyLine([[st.session_state.loc_lat, st.session_state.loc_lon], [art_lat, art_lon]], color="#3b82f6", weight=4, dash_array="10, 10").add_to(m)
                            
                            st_folium(m, height=350, use_container_width=True, key="unique_main_routing_map")
                            
                            cust_lat, cust_lon = st.session_state.loc_lat, st.session_state.loc_lon
                            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={cust_lat},{cust_lon}&destination={art_lat},{art_lon}"
                            st.markdown(f'<p style="text-align: center; margin-top: 10px;"><a href="{maps_url}" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">📍 Open Directions in Google Maps</a></p>', unsafe_allow_html=True)
                            
                            if not st.session_state.service_booked:
                                if st.button("🚀 Book Service & Confirm Drop-off" if "Option A" in workflow else "🚀 Schedule Courier Pickup", type="primary", use_container_width=True, key="book_service_btn"):
                                    booking_payload = {
                                        "customer_name": "Sai Dasaradharam G.",
                                        "item_name": item_name,
                                        "defect": diag.get("defect_type", "General Repair"),
                                        "artisan_id": artisan.get("id", "artisan_01"),
                                        "artisan_name": artisan.get("name", "Partner Shop"),
                                        "workflow": workflow,
                                        "status": "Booked - Pending Drop-off" if "Option A" in workflow else "Pickup Scheduled"
                                    }
                                    try:
                                        res = requests.post("http://127.0.0.1:8000/api/v1/book-service", json=booking_payload, timeout=5)
                                        if res.status_code == 200:
                                            st.session_state.service_booked = True
                                            st.success("Service booked successfully!")
                                            st.rerun()
                                        else:
                                            st.error("Failed to register booking with server.")
                                    except Exception as e:
                                        st.error(f"Connection error: {str(e)}")
                            else:
                                st.success("✅ Service Booked & Confirmed!")
                        except Exception as map_err:
                            st.error(f"Map rendering temporarily unavailable: {map_err}")
                    else:
                        st.warning("No qualified shops within catchment area. Item will be routed to standard returns warehouse.")

                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                # --- CONDITIONAL DISPLAY BASED ON OPTION A VS OPTION B AFTER BOOKING ---
                if st.session_state.service_booked:
                    if "Option A" in workflow:
                        with st.container(border=True):
                            st.markdown("#### 🧾 Counter Reimbursement & Fraud Guard")
                            st.info("Take your item to the shop above, get it fixed, and upload your digital repair receipt to claim your instant refund while keeping your item.")
                            
                            receipt_file = st.file_uploader("Upload Repair Receipt", type=["jpg", "jpeg", "png"], key="unique_receipt_upload")
                            if receipt_file: st.image(receipt_file, caption="Receipt Uploaded", width=250)
                            
                            if receipt_file:
                                if st.button("🛡️ Verify Receipt & Claim Refund", type="primary", use_container_width=True, key="unique_verify_btn"):
                                    with st.spinner("Executing Vertex AI Fraud Guard..."):
                                        receipt_file.seek(0)
                                        r_files = {"file": (receipt_file.name, receipt_file.getvalue(), receipt_file.type)}
                                        r_data = {"estimated_cost": str(diag.get("estimated_repair_cost_inr", 0))}
                                        r_res = requests.post("http://127.0.0.1:8000/api/v1/verify-receipt", data=r_data, files=r_files)
                                        if r_res.status_code == 200:
                                            st.session_state.receipt_verified = r_res.json()
                                        else:
                                            st.error("Failed to verify receipt.")
                                            
                            if st.session_state.receipt_verified:
                                v_data = st.session_state.receipt_verified
                                if v_data.get("status") == "VERIFIED":
                                    st.success(f"**✅ RECEIPT VERIFIED:** ₹{v_data.get('extracted_amount_inr', '0')} approved. Instant refund dispatched to bank account.")
                                else:
                                    st.error(f"**⚠️ FLAG RAISED:** {v_data.get('reason', 'Amount mismatch or invalid image.')}. Manual review triggered.")
                    else:
                        with st.container(border=True):
                            st.markdown("#### 🚚 Pickup Scheduled & Managed Logistics")
                            st.success("✅ **Pickup is scheduled!** A local courier partner has been assigned to collect your item.")
                            st.markdown("""
                            * **Status:** Dispatching rider to your pinned location.
                            * **Next Steps:** Keep your item ready. The rider will deliver it directly to the matched artisan workshop for local restoration.
                            """)
                else:
                    with st.container(border=True):
                        if "Option A" in workflow:
                            st.info("📌 **Next Step:** Click 'Book Service & Confirm Drop-off' above to unlock receipt upload.")
                        else:
                            st.info("📌 **Next Step:** Click 'Schedule Courier Pickup' above to confirm your pickup request.")