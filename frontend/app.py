import streamlit as st
import requests
import pandas as pd
from PIL import Image

st.set_page_config(
    page_title="ReRoute | Zero-Hub Reverse Triangulation",
    page_icon="🔄",
    layout="wide"
)

# Custom Styling for polished Hackathon UI
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #1E293B; margin-bottom: 0.2rem; }
    .sub-header { font-size: 1rem; color: #64748B; margin-bottom: 1.5rem; }
    .metric-card { background-color: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 16px; }
    .status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-weight: 600; font-size: 0.85rem; }
    .status-active { background-color: #DCFCE7; color: #166534; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🔄 ReRoute: Zero-Hub Reverse Triangulation</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Autonomous Agentic Reverse Logistics powered by Gemini & Google Cloud</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1], gap="large")

# ----------------- Left Column: Customer Return Portal -----------------
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
        st.image(image, caption="Return Intake Inspection View", use_container_width=True)

    process_btn = st.button("⚡ Process Autonomous Triangulation", type="primary", use_container_width=True, disabled=not uploaded_file)

# ----------------- Right Column: Multi-Agent Trace & Arbitrage -----------------
with col_right:
    st.subheader("🤖 Agent Swarm Trace & Arbitrage Ledger")
    
    if process_btn and uploaded_file:
        backend_url = "http://127.0.0.1:8000/api/v1/intercept"
        
        with st.status("Executing Autonomous Triangulation Protocol...", expanded=True) as status:
            # Accurate model reflection
            st.write("🔍 **Diagnostic Agent:** Invoking Gemini 3.8 Flash multimodal vision pipeline...")
            
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {
                "product_name": selected_product,
                "retail_price": str(retail_price),
                "customer_lat": str(customer_lat),
                "customer_lon": str(customer_lon)
            }
            
            try:
                response = requests.post(backend_url, data=data, files=files, timeout=45)
                
                if response.status_code == 200:
                    payload = response.json()
                    diag = payload.get("diagnosis", {})
                    arb = payload.get("arbitrage", {})
                    
                    st.write(f"✅ **Diagnostic Agent Complete:** Detected `{diag.get('defect_type')}` (Severity: {diag.get('severity')})")
                    st.write("📍 **Routing Agent:** Queried Firestore geospatial index for verified repair credentials...")
                    
                    artisan = arb.get("artisan_matched")
                    dist = arb.get("distance_miles")
                    
                    if artisan:
                        # Format distance cleanly
                        dist_str = f"{dist:.2f} miles" if dist and dist >= 0.1 else "Within immediate neighborhood (<0.1 mi)"
                        st.write(f"🎯 **Matched Artisan:** `{artisan.get('name')}` ({dist_str})")
                    else:
                        st.write("⚠️ **Routing Notice:** No qualified artisan within catchment radius; standard warehouse fallback applied.")
                        
                    st.write("⚖️ **Arbitrage Engine:** Evaluated reverse freight costs vs local recommerce delta.")
                    status.update(label="Triangulation & Settlement Completed!", state="complete")
                    
                    # ----------------- Results Dashboard -----------------
                    st.divider()
                    st.markdown("### 📊 Economic & Ecological Impact")
                    
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Brand Net Recovery", f"${arb.get('reroute_net_recovery', 0):.2f}", f"+${arb.get('net_savings_usd', 0):.2f} vs Hub Return")
                    m2.metric("Local Repair Bounty", f"${diag.get('estimated_repair_cost_usd', 0):.2f}", artisan.get('name', 'N/A') if artisan else "None")
                    m3.metric("Scope-3 CO₂ Avoided", f"{arb.get('avoided_co2_kg', 0):.1f} kg", "Avoided Long-haul Freight")
                    
                    st.divider()
                    st.markdown("### 🗺️ Geospatial Routing & Settlement")
                    
                    if artisan:
                        # Render dual coordinate markers for map visualization
                        map_data = pd.DataFrame([
                            {"lat": customer_lat, "lon": customer_lon, "type": "Customer"},
                            {"lat": artisan.get("latitude"), "lon": artisan.get("longitude"), "type": "Artisan"}
                        ])
                        st.map(map_data, latitude="lat", longitude="lon", size=25, zoom=12)
                        
                        st.success(
                            f"**Drop-off Partner:** {artisan.get('name')}\n\n"
                            f"* **Distance:** {dist:.2f} miles\n"
                            f"* **Turnaround Window:** {diag.get('repair_turnaround_hours', 24)} hours\n"
                            f"* **Artisan Rating:** ⭐ {artisan.get('rating', 4.8)}/5.0\n"
                            f"* **Escrow Action:** Bounty voucher held in escrow. Payout released automatically upon barcode scan at drop-off."
                        )
                    else:
                        st.warning("Item scheduled for standard consolidated reverse shipment.")
                        
                else:
                    status.update(label="API Error", state="error")
                    st.error(f"Backend returned status {response.status_code}: {response.text}")
                    
            except Exception as e:
                status.update(label="Connection Failed", state="error")
                st.error(f"Could not reach backend: {str(e)}")
    else:
        st.info("Upload an image on the left and click **Process Autonomous Triangulation** to view the live agent execution.")