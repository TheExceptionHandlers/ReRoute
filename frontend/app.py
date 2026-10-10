import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image

st.set_page_config(
    page_title="ReRoute | Zero-Hub Reverse Triangulation",
    page_icon="🔄",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .main-header {
        background: -webkit-linear-gradient(#4facfe, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 2.2rem; 
        margin-bottom: 0.2rem;
    }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 1.5rem; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🔄 ReRoute: Zero-Hub Reverse Triangulation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Agentic Reverse Logistics powered by Gemini & Google Cloud</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("📦 Customer Return Ingestion")
    
    product_options = {
        "Alpine Trail Shell Jacket": 120.00,
        "Vanguard All-Terrain Boots": 145.00,
        "Merino Wool Commuter Sweater": 85.00
    }
    
    selected_product = st.selectbox("Select Returned Item", list(product_options.keys()))
    retail_price = st.number_input("Retail Price (USD)", value=product_options[selected_product], step=5.0)
    
    customer_coords = st.columns(2)
    with customer_coords[0]:
        customer_lat = st.number_input("Customer Latitude", value=12.9716, format="%.4f")
    with customer_coords[1]:
        customer_lon = st.number_input("Customer Longitude", value=77.5946, format="%.4f")

    uploaded_file = st.file_uploader("Upload Inspection Photo (Defect/Damage)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Return Intake Inspection View", width="stretch")

    process_btn = st.button("⚡ Process Autonomous Triangulation", type="primary", width="stretch", disabled=not uploaded_file)

with col_right:
    st.subheader("🤖 Agent Swarm Trace & Arbitrage Ledger")
    
    # 1. Initialize session state to hold the payload across page refreshes
    if "payload" not in st.session_state:
        st.session_state.payload = None
    
    if process_btn and uploaded_file:
        backend_url = "http://127.0.0.1:8000/api/v1/intercept"
        
        with st.status("Executing Autonomous Triangulation Protocol...", expanded=True) as status:
            st.write("🔍 **Diagnostic Agent:** Invoking Gemini multimodal vision pipeline...")
            
            uploaded_file.seek(0)
            file_bytes = uploaded_file.getvalue()
            mime_type = uploaded_file.type if uploaded_file.type else "image/jpeg"
            files = {"file": (uploaded_file.name, file_bytes, mime_type)}
            data = {
                "product_name": selected_product,
                "retail_price": str(retail_price),
                "customer_lat": str(customer_lat),
                "customer_lon": str(customer_lon)
            }
            
            try:
                response = requests.post(backend_url, data=data, files=files, timeout=90)
                
                if response.status_code == 200:
                    # 2. Save data to session state instead of rendering immediately
                    st.session_state.payload = response.json()
                    status.update(label="Triangulation & Settlement Completed!", state="complete")
                else:
                    status.update(label="API Error", state="error")
                    st.error(f"Backend returned status {response.status_code}: {response.text}")
                    
            except Exception as e:
                status.update(label="Connection Failed", state="error")
                st.error(f"Could not reach backend: {str(e)}")

    # 3. Render the UI safely outside the button-click block
    if st.session_state.payload:
        payload = st.session_state.payload
        diag = payload.get("diagnosis", {})
        arb = payload.get("arbitrage", {})
        
        defect_name = diag.get("defect_type", "Defect identified")
        severity_name = diag.get("severity", "moderate")
        st.write(f"✅ **Diagnostic Agent Complete:** Detected `{defect_name}` (Severity: {severity_name})")
        st.write("📍 **Routing Agent:** Queried verified local artisans...")
        
        artisan = arb.get("artisan_matched")
        dist = arb.get("distance_miles")
        
        if artisan:
            dist_val = float(dist) if dist is not None else 0.0
            dist_str = f"{dist_val:.2f} miles" if dist_val >= 0.1 else "Within immediate neighborhood (<0.1 mi)"
            st.write(f"🎯 **Matched Artisan:** `{artisan.get('name', 'Local Verified Partner')}` ({dist_str})")
        else:
            st.write("⚠️ **Routing Notice:** No qualified artisan within catchment radius; standard warehouse fallback applied.")
            
        st.write("⚖️ **Arbitrage Engine:** Evaluated reverse freight costs vs local recommerce delta.")
        
        st.divider()
        st.markdown("### 📊 Economic & Ecological Impact")
        
        m1, m2, m3 = st.columns(3)
        net_rec = arb.get("reroute_net_recovery", 0.0) or 0.0
        net_sav = arb.get("net_savings_usd", 0.0) or 0.0
        rep_cost = diag.get("estimated_repair_cost_usd", 0.0) or 0.0
        co2_saved = arb.get("avoided_co2_kg", 0.0) or 0.0
        
        m1.metric("Brand Net Recovery", f"${float(net_rec):.2f}", f"+${float(net_sav):.2f} vs Hub Return")
        m2.metric("Local Repair Bounty", f"${float(rep_cost):.2f}", artisan.get("name", "N/A") if artisan else "None")
        m3.metric("Scope-3 CO₂ Avoided", f"{float(co2_saved):.1f} kg", "Avoided Long-haul Freight")
        
        st.divider()
        st.markdown("### 🗺️ Live Geospatial Routing")
        
        if artisan and artisan.get("latitude") and artisan.get("longitude"):
            try:
                m = folium.Map(location=[customer_lat, customer_lon], zoom_start=13)

                folium.Marker(
                    [customer_lat, customer_lon],
                    popup="Customer Location",
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(m)

                art_lat = float(artisan["latitude"])
                art_lon = float(artisan["longitude"])
                art_name = artisan.get("name", "Artisan Partner")
                art_rating = artisan.get("rating", 4.8)
                art_address = artisan.get("address", "Bengaluru")

                folium.Marker(
                    [art_lat, art_lon],
                    popup=f"<b>{art_name}</b><br>Rating: ⭐{art_rating}<br>{art_address}",
                    icon=folium.Icon(color="green", icon="wrench")
                ).add_to(m)

                folium.PolyLine(
                    locations=[[customer_lat, customer_lon], [art_lat, art_lon]],
                    color="#00f2fe",
                    weight=3,
                    dash_array="5, 5"
                ).add_to(m)

                st_folium(m, width=700, height=400)
                
                dist_display = f"{float(dist):.2f} miles" if dist is not None else "Local"
                turnaround = diag.get("repair_turnaround_hours", 24)
                
                st.success(
                    f"**Drop-off Partner:** {art_name}\n\n"
                    f"* **Address:** {art_address}\n"
                    f"* **Distance:** {dist_display}\n"
                    f"* **Turnaround Window:** {turnaround} hours\n"
                    f"* **Escrow Action:** Bounty voucher held in escrow. Payout released automatically upon barcode scan at drop-off."
                )
            except Exception as map_err:
                st.error(f"Map display notice: {map_err}")
                st.json(arb)
        else:
            st.warning("Item scheduled for standard consolidated reverse shipment.")