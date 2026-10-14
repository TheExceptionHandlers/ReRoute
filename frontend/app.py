import streamlit as st
import requests
import folium
from streamlit_folium import st_folium
from PIL import Image
from streamlit_geolocation import streamlit_geolocation

# --- STATE MANAGEMENT ---
if "payload" not in st.session_state:
    st.session_state.payload = None
if "loc_lat" not in st.session_state:
    st.session_state.loc_lat = 12.9716
if "loc_lon" not in st.session_state:
    st.session_state.loc_lon = 77.5946
if "loc_address" not in st.session_state:
    st.session_state.loc_address = ""
if "last_gps_fetch" not in st.session_state:
    st.session_state.last_gps_fetch = None
if "needs_confirmation" not in st.session_state:
    st.session_state.needs_confirmation = False
if "location_confirmed" not in st.session_state:
    st.session_state.location_confirmed = False
if "manual_override" not in st.session_state:
    st.session_state.manual_override = False
if "manual_address" not in st.session_state:
    st.session_state.manual_address = ""

# --- GEOCODING HELPERS (Free OpenStreetMap API) ---
def reverse_geocode(lat, lon):
    """Converts Map Coordinates to Street Address"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        headers = {'User-Agent': 'ReRoute-Enterprise-Dashboard/1.0'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            return res.json().get('display_name', 'Address not found')
    except Exception:
        pass
    return f"Lat: {lat:.5f}, Lon: {lon:.5f}"

def forward_geocode(address):
    """Converts Typed Address to Map Coordinates"""
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json&limit=1"
        headers = {'User-Agent': 'ReRoute-Enterprise-Dashboard/1.0'}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 0:
            data = res.json()[0]
            return float(data['lat']), float(data['lon'])
    except Exception:
        pass
    return None, None

def sync_manual_input():
    """Callback triggered when user hits Enter in the manual address box"""
    addr = st.session_state.manual_address
    if addr:
        lat, lon = forward_geocode(addr)
        if lat and lon:
            st.session_state.loc_lat = lat
            st.session_state.loc_lon = lon
            st.session_state.loc_address = addr

# --- MODAL DIALOG (Auto-Detect Confirmation) ---
@st.dialog("📍 Confirm Auto-Detected Location")
def location_confirmation_dialog():
    st.markdown(f"**Detected Address:**\n{st.session_state.loc_address}")
    st.caption("🖱️ **Zoom in and click anywhere on the map** to adjust your exact location.")
    
    try:
        preview_map = folium.Map(
            location=[st.session_state.loc_lat, st.session_state.loc_lon], 
            zoom_start=17, 
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="Google Maps"
        )
        folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], icon=folium.Icon(color="red", icon="user")).add_to(preview_map)
        map_data = st_folium(preview_map, height=300, use_container_width=True, key="dialog_map", returned_objects=["last_clicked"])
        
        if map_data and map_data.get("last_clicked"):
            c_lat = map_data["last_clicked"]["lat"]
            c_lon = map_data["last_clicked"]["lng"]
            if round(c_lat, 5) != round(st.session_state.loc_lat, 5):
                st.session_state.loc_lat = c_lat
                st.session_state.loc_lon = c_lon
                st.session_state.loc_address = reverse_geocode(c_lat, c_lon)
                st.rerun()
    except Exception:
        st.caption("Map preview unavailable.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ Enter Manually", use_container_width=True):
            st.session_state.needs_confirmation = False
            st.session_state.manual_override = True
            st.session_state.manual_address = st.session_state.loc_address 
            st.rerun()
    with col2:
        if st.button("✅ Confirm Location", type="primary", use_container_width=True):
            st.session_state.needs_confirmation = False
            st.session_state.location_confirmed = True
            st.rerun()

# --- PAGE UI & STYLING ---
st.set_page_config(page_title="ReRoute | Zero-Hub Reverse Logistics", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; background-color: #f8fafc; color: #0f172a; }
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #94a3b8 !important; border-radius: 8px !important; background-color: #ffffff !important; padding: 24px !important; }
    .metric-wrapper { background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; text-align: center; height: 100%; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; color: #64748b; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #0f172a; margin: 0; }
    .metric-value.positive { color: #10b981; }
    .status-banner { font-family: 'JetBrains Mono', monospace; padding: 14px 20px; border-radius: 6px; font-weight: 700; margin-bottom: 24px; font-size: 0.9rem; display: flex; gap: 10px; }
    .status-idle { background-color: #f1f5f9; color: #475569; border: 1px solid #cbd5e1; }
    .status-active { background-color: #ecfdf5; color: #059669; border: 1px solid #34d399; }
</style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, positive=False):
    return f'<div class="metric-wrapper"><div class="metric-label">{label}</div><p class="metric-value{" positive" if positive else ""}">{value}</p></div>'

st.title("ReRoute")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -10px; margin-bottom: 2rem;'>Autonomous Multi-Agent Reverse Logistics Dashboard</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.4], gap="large")

# --- LEFT COLUMN: INPUTS ---
with col_left:
    with st.container(border=True):
        st.markdown("##### 📦 Item Particulars")
        c1, c2 = st.columns(2)
        with c1:
            product_options = {"Alpine Trail Shell Jacket": 120.00, "Vanguard All-Terrain Boots": 145.00, "Merino Wool Commuter Sweater": 85.00}
            selected_product = st.selectbox("Select Returned Item", list(product_options.keys()), label_visibility="collapsed")
        with c2:
            retail_price = st.number_input("Retail Price (USD)", value=product_options[selected_product], format="%.2f")
    
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("##### 📍 Drop-off Coordinates")
        
        # 1. Device GPS Fetch
        gps_data = streamlit_geolocation()
        if gps_data and gps_data.get('latitude'):
            current_gps = f"{gps_data['latitude']},{gps_data['longitude']}"
            if current_gps != st.session_state.last_gps_fetch:
                st.session_state.last_gps_fetch = current_gps
                st.session_state.loc_lat = float(gps_data['latitude'])
                st.session_state.loc_lon = float(gps_data['longitude'])
                st.session_state.loc_address = reverse_geocode(st.session_state.loc_lat, st.session_state.loc_lon)
                st.session_state.needs_confirmation = True
                st.session_state.manual_override = False 
                st.rerun()

        if st.session_state.needs_confirmation:
            location_confirmation_dialog()

        # 2. Main Logic Flow for Location UI
        if st.session_state.location_confirmed:
            st.success("✅ Location Confirmed")
            st.text_area("📝 Confirmed Address", value=st.session_state.loc_address, height=68, disabled=True)
            if st.button("🔄 Edit / Change Location"):
                st.session_state.location_confirmed = False
                st.session_state.manual_override = True
                st.rerun()
                
        elif st.session_state.manual_override:
            st.warning("✏️ **Manual Entry Mode:** Type an address below (press Enter) OR click the map to drop a pin.")
            
            # Text input tied to forward geocoding
            st.text_input("Search Address:", key="manual_address", on_change=sync_manual_input)
            
            try:
                # Interactive Map
                m_map = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], icon=folium.Icon(color="blue", icon="info-sign")).add_to(m_map)
                
                m_data = st_folium(m_map, height=300, use_container_width=True, key="manual_map", returned_objects=["last_clicked"])
                
                # If map is clicked, reverse geocode and update text box
                if m_data and m_data.get("last_clicked"):
                    c_lat = m_data["last_clicked"]["lat"]
                    c_lon = m_data["last_clicked"]["lng"]
                    if round(c_lat, 5) != round(st.session_state.loc_lat, 5):
                        st.session_state.loc_lat = c_lat
                        st.session_state.loc_lon = c_lon
                        new_addr = reverse_geocode(c_lat, c_lon)
                        st.session_state.loc_address = new_addr
                        st.session_state.manual_address = new_addr
                        st.rerun()
            except Exception:
                st.caption("Map preview unavailable.")
                
            if st.button("✅ Confirm Location", type="primary", use_container_width=True):
                st.session_state.location_confirmed = True
                st.session_state.manual_override = False
                st.rerun()
        else:
            st.info("👆 Click the location button above to detect and confirm your coordinates.")

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("##### 🔍 Defect Telemetry")
        uploaded_file = st.file_uploader("Upload inspection image (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file:
            st.image(Image.open(uploaded_file), caption="Intake Feed Locked", use_container_width=True)

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    process_btn = st.button("⚡ Initialize Agent Swarm Execution", use_container_width=True, type="primary", disabled=not (uploaded_file and st.session_state.location_confirmed))

# --- RIGHT COLUMN: METRICS & ROUTING ---
with col_right:
    if process_btn and uploaded_file:
        st.session_state.payload = None 
        backend_url = "http://127.0.0.1:8000/api/v1/intercept"
        
        with st.status("Executing Agentic Logistics Pipeline...", expanded=True) as status:
            st.write("Initializing Diagnostic Agent...")
            uploaded_file.seek(0)
            file_bytes = uploaded_file.getvalue()
            files = {"file": (uploaded_file.name, file_bytes, uploaded_file.type or "image/jpeg")}
            
            data = {
                "product_name": selected_product, 
                "retail_price": str(retail_price), 
                "customer_lat": str(st.session_state.loc_lat), 
                "customer_lon": str(st.session_state.loc_lon),
                "customer_address": st.session_state.loc_address
            }
            try:
                response = requests.post(backend_url, data=data, files=files, timeout=90)
                if response.status_code == 200:
                    st.session_state.payload = response.json()
                    status.update(label="Triangulation Protocol Complete", state="complete")
                    st.rerun() # FORCES UI TO REFRESH WITH METRICS
                else:
                    status.update(label="API Handshake Failed", state="error")
                    st.error(f"Backend Error [{response.status_code}]: {response.text}")
            except Exception as e:
                status.update(label="Network Timeout", state="error")
                st.error(f"Could not reach backend server: {str(e)}\n\nMake sure your FastAPI server is running on port 8000!")

    if st.session_state.payload:
        st.markdown('<div class="status-banner status-active">● SYSTEM STATUS: ARBITRAGE LOCKED & ROUTED</div>', unsafe_allow_html=True)
        payload = st.session_state.payload
        diag = payload.get("diagnosis", {})
        arb = payload.get("arbitrage", {})
        artisan = arb.get("artisan_matched", {})
        
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(render_metric_card("Arbitrage Spread", f"${arb.get('net_savings_usd', 0.0):.2f}", positive=True), unsafe_allow_html=True)
        with mc2: st.markdown(render_metric_card("Carbon Prevented", f"{arb.get('avoided_co2_kg', 0.0):.1f}kg", positive=True), unsafe_allow_html=True)
        with mc3:
            dist = arb.get('distance_miles')
            dist_display = f"{float(dist):.2f}mi" if dist is not None else "Local"
            st.markdown(render_metric_card("Routing Radius", dist_display), unsafe_allow_html=True)
            
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("##### 🗺️ Geospatial Drop-off Telemetry")
            if artisan and artisan.get("latitude") and artisan.get("longitude"):
                st.info(
                    f"**Matched Partner:** {artisan.get('name', 'Artisan Partner')} | **SLA:** {diag.get('repair_turnaround_hours', 24)}h\n\n"
                    f"**Address:** {artisan.get('address', 'N/A')}\n\n"
                    f"**Defect Identified:** {str(diag.get('defect_type', 'Unknown')).replace('_', ' ').title()}"
                )
                try:
                    m = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                    folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Customer Origin", icon=folium.Icon(color="red", icon="user")).add_to(m)
                    art_lat, art_lon = float(artisan["latitude"]), float(artisan["longitude"])
                    folium.Marker([art_lat, art_lon], popup=f"<b>{artisan.get('name')}</b>", icon=folium.Icon(color="green", icon="wrench")).add_to(m)
                    folium.PolyLine([[st.session_state.loc_lat, st.session_state.loc_lon], [art_lat, art_lon]], color="#3b82f6", weight=4, dash_array="10, 10").add_to(m)
                    st_folium(m, height=400, use_container_width=True, key="main_routing_map")
                except Exception as map_err:
                    st.error(f"Geospatial rendering temporarily unavailable: {map_err}")
            else:
                st.warning("No qualified artisans within catchment area. Defaulting to consolidated standard warehouse freight.")
    else:
        st.markdown('<div class="status-banner status-idle">○ SYSTEM STATUS: AWAITING INGESTION</div>', unsafe_allow_html=True)
        mc1, mc2, mc3 = st.columns(3)
        with mc1: st.markdown(render_metric_card("Arbitrage Spread", "—"), unsafe_allow_html=True)
        with mc2: st.markdown(render_metric_card("Carbon Prevented", "—"), unsafe_allow_html=True)
        with mc3: st.markdown(render_metric_card("Routing Radius", "—"), unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.info("The dashboard is idling. Awaiting defect telemetry upload and swarm initialization to calculate real-time routing metrics.")