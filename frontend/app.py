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
if "loc_lat" not in st.session_state: st.session_state.loc_lat = 12.9716
if "loc_lon" not in st.session_state: st.session_state.loc_lon = 77.5946
if "loc_address" not in st.session_state: st.session_state.loc_address = "Koramangala 4th Block, Bengaluru, India"
if "location_locked" not in st.session_state: st.session_state.location_locked = True
if "uploaded_bytes" not in st.session_state: st.session_state.uploaded_bytes = None
if "uploaded_name" not in st.session_state: st.session_state.uploaded_name = None
if "uploaded_type" not in st.session_state: st.session_state.uploaded_type = None
if "receipt_verified" not in st.session_state: st.session_state.receipt_verified = None
if "last_clicked_lat" not in st.session_state: st.session_state.last_clicked_lat = None
if "last_clicked_lon" not in st.session_state: st.session_state.last_clicked_lon = None
if "loc_search_bar" not in st.session_state: st.session_state.loc_search_bar = ""
if "selected_workflow_state" not in st.session_state: st.session_state.selected_workflow_state = "Option A: Self Drop-off (Get Instant Refund)"

# --- GEOCODING HELPERS ---
def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1"
        res = requests.get(url, headers={'User-Agent': 'ReRoute/1.0'}, timeout=5)
        if res.status_code == 200: return res.json().get('display_name', 'Address not found')
    except Exception: pass
    return f"Lat: {lat:.5f}, Lon: {lon:.5f}"

def forward_geocode(address):
    try:
        query = address if "bengaluru" in address.lower() or "bangalore" in address.lower() else f"{address}, Bengaluru, India"
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': query, 'format': 'json', 'limit': 1}
        res = requests.get(url, params=params, headers={'User-Agent': 'ReRoute/1.0'}, timeout=5)
        if res.status_code == 200 and len(res.json()) > 0:
            return float(res.json()[0]['lat']), float(res.json()[0]['lon'])
    except Exception: pass
    return None, None

# --- PAGE UI & STYLING ---
st.set_page_config(page_title="ReRoute | Smart Returns", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; }
    [data-testid="stFileUploadDropzone"] { border: 2px dashed #475569 !important; border-radius: 8px !important; background-color: #0f172a !important; padding: 24px !important; transition: all 0.2s; }
    [data-testid="stFileUploadDropzone"]:hover { border-color: #3b82f6 !important; background-color: #1e293b !important; }
    
    .metric-wrapper { background-color: #1e293b; border: 1px solid #334155; border-radius: 8px; padding: 20px; text-align: center; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    .metric-label { font-size: 0.75rem; text-transform: uppercase; color: #94a3b8; font-weight: 600; margin-bottom: 8px; }
    .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 700; color: #f8fafc; margin: 0; }
    .metric-value.positive { color: #34d399; }
    .status-banner { font-family: 'JetBrains Mono', monospace; padding: 14px 20px; border-radius: 6px; font-weight: 700; margin-bottom: 24px; font-size: 0.9rem; display: flex; gap: 10px; }
    .status-active { background-color: #064e3b; color: #34d399; border: 1px solid #059669; }
    .lifecycle-step { background-color: #0f172a; border-left: 4px solid #3b82f6; padding: 12px 16px; margin-bottom: 10px; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

def render_metric_card(label, value, positive=False):
    return f'<div class="metric-wrapper"><div class="metric-label">{label}</div><p class="metric-value{" positive" if positive else ""}">{value}</p></div>'

st.title("ReRoute")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -10px; margin-bottom: 1rem;'>Autonomous Multi-Agent Reverse Logistics Dashboard</p>", unsafe_allow_html=True)

tab_customer, tab_enterprise = st.tabs(["🛒 Customer Return Portal", "📈 Enterprise Mission Control"])

with tab_enterprise:
    st.markdown("### Executive Savings Overview (Last 30 Days)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Items Diverted Locally", "12,482", "+14%")
    m2.metric("Logistics Cost Saved", "₹48.5L", "+22%")
    m3.metric("Scope-3 CO₂ Prevented", "14.2 Tons", "+8%")
    m4.metric("Active Local Artisans", "843", "+42")
    
    st.divider()
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("**Daily Freight Avoidance Savings (₹)**")
        chart_data = pd.DataFrame(np.random.randn(30, 1) * 10000 + 150000, columns=["Savings"])
        st.line_chart(chart_data)
    with col_chart2:
        st.markdown("**Returns by Defect Category**")
        defect_data = pd.DataFrame({"Category": ["Zippers", "Tears/Seams", "Soles", "Electronics"], "Count": [4500, 3200, 2100, 2682]}).set_index("Category")
        st.bar_chart(defect_data)

with tab_customer:
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
                st.session_state.selected_workflow_state = selected_workflow
                st.divider()
                st.markdown("##### 📍 Verify Your Location")
                st.caption("Search an address or click directly on the map below.")
                
                col_s1, col_s2 = st.columns([3, 1], vertical_alignment="bottom")
                with col_s1:
                    search_input = st.text_input("Search Address:", value=st.session_state.loc_address, key="loc_search_bar")
                with col_s2:
                    search_clicked = st.button("🔍 Set", use_container_width=True, key="search_btn")

                if search_clicked and search_input:
                    lat, lon = forward_geocode(search_input)
                    if lat and lon:
                        st.session_state.loc_lat = lat
                        st.session_state.loc_lon = lon
                        st.session_state.loc_address = search_input
                        st.success(f"Locked: {search_input}")
                        st.rerun()

                try:
                    m_map = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=15, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                    folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Selected Location", icon=folium.Icon(color="red", icon="user")).add_to(m_map)
                    
                    m_data = st_folium(m_map, height=250, use_container_width=True, key="primary_map", returned_objects=["last_clicked"])
                    
                    if m_data and m_data.get("last_clicked"):
                        c_lat = m_data["last_clicked"]["lat"]
                        c_lon = m_data["last_clicked"]["lng"]
                        if round(c_lat, 4) != round(st.session_state.loc_lat, 4):
                            st.session_state.loc_lat = c_lat
                            st.session_state.loc_lon = c_lon
                            new_addr = reverse_geocode(c_lat, c_lon)
                            st.session_state.loc_address = new_addr
                            st.session_state.loc_search_bar = new_addr
                            st.rerun()
                except Exception:
                    st.caption("Map preview unavailable.")

                st.success(f"✅ Active Location: {st.session_state.loc_address}")

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
                st.write(f"**Method:** {st.session_state.selected_workflow_state}")
            if st.button("🔄 Start New Return", use_container_width=True):
                st.session_state.payload = None
                st.session_state.uploaded_bytes = None
                st.rerun()

        with col_right:
            payload = st.session_state.payload
            diag = payload.get("diagnosis", {})
            is_repairable = diag.get("is_repairable", True)
            workflow = st.session_state.selected_workflow_state

            if not is_repairable:
                st.markdown('<div class="status-banner" style="background-color: #450a0a; color: #fca5a5; border: 1px solid #b91c1c;">● SYSTEM STATUS: TOTAL LOSS - ROUTED TO SALVAGE</div>', unsafe_allow_html=True)
                st.error(f"**AI Diagnosis (Unrepairable):** {diag.get('defect_summary', 'Item is damaged beyond functional restoration limits.')}")
            else:
                # --- DISTINCT VISUAL THEME BASED ON WORKFLOW ---
                if "Option A" in workflow:
                    st.markdown('<div class="status-banner" style="background-color: #0f2830; color: #38bdf8; border: 1px solid #0284c7;">⚡ WORKFLOW ACTIVE: SELF DROP-OFF & INSTANT REIMBURSEMENT</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-banner" style="background-color: #3b1f0c; color: #fb923c; border: 1px solid #f97316;">🚚 WORKFLOW ACTIVE: MANAGED COURIER PICKUP & RECOMMERCE</div>', unsafe_allow_html=True)

                raw_arb = payload.get("arbitrage", {})
                arb = raw_arb.get("match_artisan_and_arbitrage_response", raw_arb)
                artisan = arb.get("artisan_matched", {})
                
                # --- MAP & PARTNER DETAILS ---
                with st.container(border=True):
                    st.markdown("##### 🗺️ Local Repair Partner Details")
                    if artisan and artisan.get("latitude") and artisan.get("longitude"):
                        st.info(f"**Matched Shop:** {artisan.get('name', 'Artisan Partner')} | **Estimated Turnaround:** {diag.get('repair_turnaround_hours', 24)}h\n\n**Address:** {artisan.get('address', 'N/A')}\n\n**AI Diagnosis:** {str(diag.get('defect_type', 'Unknown')).replace('_', ' ').title()} - {diag.get('defect_summary', '')}")
                        try:
                            m = folium.Map(location=[st.session_state.loc_lat, st.session_state.loc_lon], zoom_start=14, tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}", attr="Google Maps")
                            folium.Marker([st.session_state.loc_lat, st.session_state.loc_lon], popup="Customer Location", icon=folium.Icon(color="red", icon="user")).add_to(m)
                            art_lat, art_lon = float(artisan["latitude"]), float(artisan["longitude"])
                            folium.Marker([art_lat, art_lon], popup=f"<b>{artisan.get('name')}</b>", icon=folium.Icon(color="green", icon="wrench")).add_to(m)
                            folium.PolyLine([[st.session_state.loc_lat, st.session_state.loc_lon], [art_lat, art_lon]], color="#3b82f6", weight=4, dash_array="10, 10").add_to(m)
                            
                            st_folium(m, height=350, use_container_width=True, key="unique_main_routing_map")
                            
                            cust_lat, cust_lon = st.session_state.loc_lat, st.session_state.loc_lon
                            maps_url = f"https://www.google.com/maps/dir/?api=1&origin={cust_lat},{cust_lon}&destination={art_lat},{art_lon}"
                            st.markdown(f'<p style="text-align: center; margin-top: 10px;"><a href="{maps_url}" target="_blank" style="color: #38bdf8; text-decoration: none; font-weight: 600;">📍 Open Directions in Google Maps</a></p>', unsafe_allow_html=True)
                        except Exception as map_err:
                            st.error(f"Map rendering temporarily unavailable: {map_err}")
                    else:
                        st.warning("No qualified shops within catchment area. Item will be routed to standard returns warehouse.")

                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                # --- DISTINCT BOTTOM SECTIONS BASED ON OPTION A VS OPTION B ---
                if "Option A" in workflow:
                    with st.container(border=True):
                        st.markdown("#### 🧾 Option A: Counter Reimbursement & Fraud Guard")
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
                        st.markdown("#### 🛒 Option B: Managed Logistics & Recommerce Listing")
                        st.success("🚚 **Courier Dispatched:** Local gig-partner assigned for doorstep pickup.")
                        shop_name = artisan.get('name', 'Partner Shop')
                        st.markdown(f"""
                        * **Step 1:** Courier collects item from your address and drops it at **{shop_name}**.
                        * **Step 2:** Artisan completes the repair and triggers escrow payout.
                        * **Step 3:** Restored item is routed directly to the **nearest micro-warehouse** (bypassing national mega-hubs).
                        * **Step 4:** Immediately listed on the platform's **"Open-Box" Marketplace** for local next-day delivery.
                        """)