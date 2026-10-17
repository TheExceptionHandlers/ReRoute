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

# --- GEOCODING HELPERS ---
def reverse_geocode(lat, lon):
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
    addr = st.session_state.manual_address
    if addr:
        lat, lon = forward_geocode(addr)
        if lat and lon:
            st.session_state.loc_lat = lat
            st.session_state.loc_lon = lon
            st.session_state.loc_address = addr

# --- MODAL DIALOG ---
@st.dialog("📍 Confirm Your Location")
def location_confirmation_dialog():
    st.markdown(f"**Detected Address:**\n{st.session_state.loc_address}")
    st.caption("🖱️ **Zoom in and click anywhere on the map** to adjust your exact location.")
    
    try:
        preview_map = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=17, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
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
st.set_page_config(page_title="ReRoute | Smart Returns", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    /* Let Streamlit's config.toml handle the main background and text colors */
    .stApp { font-family: 'Inter', sans-serif; }
    
    /* Dark Theme File Uploader Override */
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #475569 !important; border-radius: 8px !important; background-color: #0f172a !important; padding: 24px !important; transition: all 0.2s; }
    [data-testid="stFileUploadDropzone"]:hover { border-color: #3b82f6 !important; background-color: #1e293b !important; }

    /* Custom Metric Cards for Dark Theme */
    .metric-wrapper { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #f8fafc; margin: 0; }
    .metric-value.positive { color: #34d399; }
    
    /* Status Banners */
    .status-banner { font-family: 'JetBrains Mono', monospace; padding: 14px 20px; border-radius: 6px; font-weight: 700; margin-bottom: 24px; font-size: 0.9rem; display: flex; gap: 10px; }
    .status-active { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
    
    /* Lifecycle Steps */
    .lifecycle-step { background-color: #0f172a; border-left: 4px solid #3b82f6; padding: 12px 16px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, positive=False):
    return f'<div class="metric-wrapper"><div class="metric-label">{label}</div><p class="metric-value{" positive" if positive else ""}">{value}</p></div>'

st.title("ReRoute")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -10px; margin-bottom: 2rem;'>Smart Local Returns & Exchanges</p>", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.4], gap="large")

# --- LEFT COLUMN: INPUTS ---
with col_left:
    with st.container(border=True):
        st.markdown("##### 📦 Step 1: Return Details")
        c1, c2 = st.columns(2)
        with c1:
            product_options = {"Alpine Trail Shell Jacket": 8500.00, "Vanguard All-Terrain Boots": 12000.00, "Merino Wool Commuter Sweater": 4500.00}
            selected_product = st.selectbox("Select Item to Return", list(product_options.keys()), label_visibility="collapsed")
        with c2:
            retail_price = st.number_input("Retail Price (₹)", value=product_options[selected_product], format="%.2f")
    
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("##### 🚚 Step 2: Return Method")
        selected_workflow = st.radio(
            "How would you like to return this?",
            ["Option A: Self Drop-off (Get Instant Refund)", "Option B: Schedule a Pickup"],
            help="Choose self drop-off for immediate resolution, or schedule a pickup for convenience."
        )
        st.divider()
        st.markdown("##### 📍 Verify Your Location")
        
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

        if st.session_state.location_confirmed:
            st.success("✅ Location Confirmed")
            st.text_area("📝 Confirmed Address", value=st.session_state.loc_address, height=68, disabled=True)
            if st.button("🔄 Edit / Change Location"):
                st.session_state.location_confirmed = False
                st.session_state.manual_override = True
                st.rerun()
                
        elif st.session_state.manual_override:
            st.warning("✏️ **Manual Entry Mode:** Type an address below (press Enter) OR click the map to drop a pin.")
            st.text_input("Search Address:", key="manual_address", on_change=sync_manual_input)
            try:
                m_map = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], icon=folium.Icon(color="blue", icon="info-sign")).add_to(m_map)
                m_data = st_folium(m_map, height=300, use_container_width=True, key="manual_map", returned_objects=["last_clicked"])
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
        st.markdown("##### 📸 Step 3: Upload Item Photo")
        uploaded_file = st.file_uploader("Upload a photo of the damage (JPG/PNG)", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
        if uploaded_file:
            st.image(Image.open(uploaded_file), caption="Photo Uploaded Successfully", use_container_width=True)

    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    process_btn = st.button("⚡ Analyze Return & Find Local Repair", use_container_width=True, type="primary", disabled=not (uploaded_file and st.session_state.location_confirmed))

# --- RIGHT COLUMN: DYNAMIC RESULTS ONLY ---
with col_right:
    if process_btn and uploaded_file:
        st.session_state.payload = None 
        backend_url = "http://127.0.0.1:8000/api/v1/intercept"
        
        with st.status("Analyzing photo and locating nearest verified repair partner...", expanded=True) as status:
            st.write("Initializing Smart Diagnostics...")
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
                    status.update(label="Analysis Complete", state="complete")
                    st.rerun()
                else:
                    status.update(label="Connection Failed", state="error")
                    st.error(f"Backend Error [{response.status_code}]: {response.text}")
            except Exception as e:
                status.update(label="Network Timeout", state="error")
                st.error(f"Could not reach backend server: {str(e)}\n\nMake sure your FastAPI server is running on port 8000!")

    if st.session_state.payload:
        payload = st.session_state.payload
        diag = payload.get("diagnosis", {})
        is_repairable = diag.get("is_repairable", True)

        if not is_repairable:
            st.markdown('<div class="status-banner" style="background-color: #450a0a; color: #fca5a5; border: 1px solid #b91c1c;">● SYSTEM STATUS: TOTAL LOSS - ROUTED TO SALVAGE</div>', unsafe_allow_html=True)
            st.error(f"**AI Diagnosis (Unrepairable):** {diag.get('defect_summary', 'Item is damaged beyond functional restoration limits.')}")
            
            with st.container(border=True):
                st.markdown("#### Salvage & Liquidation Plan")
                st.markdown("<div class='lifecycle-step' style='border-left-color: #ef4444;'>🛑 <b>Triage Triggered:</b> Item flagged as non-repairable. Escrow and routing networks bypassed.</div>", unsafe_allow_html=True)
                st.markdown("<div class='lifecycle-step' style='border-left-color: #ef4444;'>♻️ <b>Recycling Protocol:</b> Customer instructed to discard item locally or drop at nearest textile/e-waste recycling point.</div>", unsafe_allow_html=True)
                st.markdown("<div class='lifecycle-step' style='border-left-color: #ef4444;'>💳 <b>Immediate Settlement:</b> Instant refund issued. 100% of reverse-freight shipping costs avoided for dead inventory.</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-banner status-active">● REPAIR PARTNER FOUND & ROUTED</div>', unsafe_allow_html=True)
            
            raw_arb = payload.get("arbitrage", {})
            arb = raw_arb.get("match_artisan_and_arbitrage_response", raw_arb)
            artisan = arb.get("artisan_matched", {})
            
            # Enterprise Metrics
            st.markdown("#### Enterprise Savings Dashboard")
            mc1, mc2, mc3 = st.columns(3)
            with mc1: st.markdown(render_metric_card("Net Savings", f"₹{arb.get('net_savings_usd', 0.0):.2f}", positive=True), unsafe_allow_html=True)
            with mc2: st.markdown(render_metric_card("CO₂ Saved", f"{arb.get('avoided_co2_kg', 0.0):.1f}kg", positive=True), unsafe_allow_html=True)
            with mc3:
                dist = arb.get('distance_miles')
                dist_display = f"{float(dist):.2f} km" if dist is not None else "Local"
                st.markdown(render_metric_card("Routing Distance", dist_display), unsafe_allow_html=True)
                
            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)
            
            # Dynamic Lifecycle Render
            with st.container(border=True):
                st.markdown(f"#### Return Plan: {selected_workflow.split(':')[0]}")
                
                if "Option A" in selected_workflow:
                    st.markdown("<div class='lifecycle-step'>🚶‍♂️ <b>You Drop It Off:</b> Take the item to the verified repair shop mapped below.</div>", unsafe_allow_html=True)
                    st.markdown("<div class='lifecycle-step'>🛠️ <b>Quick Fix:</b> The shop fixes the defect. Scan your app's QR code at the counter.</div>", unsafe_allow_html=True)
                    st.markdown("<div class='lifecycle-step'>💳 <b>Instant Refund:</b> We instantly refund your repair cost. You keep the fixed item!</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div class='lifecycle-step'>🚚 <b>We Pick It Up:</b> A delivery partner collects the item from your doorstep.</div>", unsafe_allow_html=True)
                    st.markdown("<div class='lifecycle-step'>🛠️ <b>Local Repair:</b> It is dropped off at the local repair shop and fully restored.</div>", unsafe_allow_html=True)
                    st.markdown("<div class='lifecycle-step'>🛒 <b>Local Resale:</b> Instead of shipping it back to a warehouse, we list it locally for next-day delivery to a new buyer.</div>", unsafe_allow_html=True)

            st.markdown("<div style='margin-bottom: 24px;'></div>", unsafe_allow_html=True)

            with st.container(border=True):
                st.markdown("##### 🗺️ Local Repair Partner Details")
                if artisan and artisan.get("latitude") and artisan.get("longitude"):
                    st.info(
                        f"**Matched Shop:** {artisan.get('name', 'Artisan Partner')} | **Estimated Turnaround:** {diag.get('repair_turnaround_hours', 24)}h\n\n"
                        f"**Address:** {artisan.get('address', 'N/A')}\n\n"
                        f"**AI Diagnosis:** {str(diag.get('defect_type', 'Unknown')).replace('_', ' ').title()} - {diag.get('defect_summary', '')}"
                    )
                    try:
                        m = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                        folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Customer Location", icon=folium.Icon(color="red", icon="user")).add_to(m)
                        art_lat, art_lon = float(artisan["latitude"]), float(artisan["longitude"])
                        folium.Marker([art_lat, art_lon], popup=f"<b>{artisan.get('name')}</b>", icon=folium.Icon(color="green", icon="wrench")).add_to(m)
                        folium.PolyLine([[st.session_state.loc_lat, st.session_state.loc_lon], [art_lat, art_lon]], color="#3b82f6", weight=4, dash_array="10, 10").add_to(m)
                        st_folium(m, height=400, use_container_width=True, key="main_routing_map")
                    except Exception as map_err:
                        st.error(f"Map rendering temporarily unavailable: {map_err}")
                else:
                    st.warning("No qualified shops within catchment area. Item will be routed to standard returns warehouse.")