# 🔄 ReRoute: Autonomous Zero-Hub Reverse Triangulation Engine

> **Eliminating traditional return mega-hubs through real-time multimodal AI triage and hyper-local artisan routing.**

[![Google Cloud Run](https://img.shields.io/badge/Cloud%20Run-Serverless-blue?logo=google-cloud)](https://cloud.google.com/run)
[![Vertex AI](https://img.shields.io/badge/Vertex%20AI-Gemini%202.5%20Flash-orange?logo=google)](https://cloud.google.com/vertex-ai)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit)](https://streamlit.io/)

---

## 🚀 Overview

Traditional e-commerce reverse logistics ship damaged or defective goods hundreds of miles back to centralized mega-hubs, destroying up to 70% of retail value through freight overhead and liquidation markdowns while generating massive, unnecessary Scope-3 carbon emissions.

**ReRoute** is an enterprise-grade, multi-agent reverse logistics platform that solves this crisis. By deploying an autonomous AI swarm at the edge, ReRoute instantly diagnoses return defects via computer vision and triangulates items directly to verified neighborhood artisans (e.g., local tailors or cobblers) within 24 hours.

---

## 🌟 Key Features & Multi-Role Ecosystem

ReRoute operates as a complete, closed-loop two-sided B2B marketplace featuring dedicated operational portals:

1. **🛒 Customer Return Portal**
   - Interactive map pin-drop and geolocation hardware sync.
   - Multimodal photo upload for instant damage inspection.
   - **Dual-Path Fulfillment:** choose between:
     - **Option A:** self drop-off with instant reimbursement via AI Fraud Guard.
     - **Option B:** managed courier pickup for local recommerce.
2. **🛠️ Artisan Partner Portal**
   - Incoming job queues, repair ETA tracking, and task milestone progression (*Accept & Start Repair* ➔ *Mark Repair Complete*).
3. **🚚 Delivery Partner Portal**
   - Field assignment tracking for managed courier pickups, displaying precise customer pickup coordinates and artisan handoff points.
4. **📈 Enterprise Mission Control & Treasury**
   - Executive telemetry dashboard tracking items diverted locally, freight savings, and carbon reduction, backed by a corporate finance escrow payout ledger.

---

## 🤖 Google AI & Cloud Stack Integration

ReRoute leverages the deep Google Cloud and AI ecosystem for production-grade reliability:

- **Gemini 2.5 Flash on Vertex AI:** powers the multimodal **Diagnostic Agent** for instant defect classification and severity scoring, as well as the **Fraud Guard Agent** for automated OCR receipt and invoice verification.
- **Google ADK 2.0 (Agent Development Kit):** orchestrates asynchronous multi-agent task execution using `InMemoryRunner` and autonomous tool calling.
- **Google Maps & Places APIs:** high-precision geospatial geocoding, distance calculations via the Haversine formula, and radius matching.
- **Google Cloud Run:** elastic, serverless containerized deployment with zero-idle billing.
- **Google Cloud Firestore:** secure NoSQL serverless document database maintaining persistent audit trails of return tickets and escrow records.

---

## 📁 Project Structure

```text
ReRoute-AI/
├── backend/
│   ├── agents/
│   │   ├── diagnostic.py      # Gemini multimodal vision inspection
│   │   ├── routing.py         # Geospatial arbitrage & artisan matching
│   │   └── fraud_guard.py     # OCR receipt verification agent
│   ├── database.py            # Google Cloud Firestore client & models
│   └── main.py                # FastAPI asynchronous endpoints
├── frontend/
│   └── app.py                 # Multi-role Streamlit reactive dashboard
├── Dockerfile                 # Container packaging for Google Cloud Run
├── requirements.txt           # Python dependencies
└── start.sh                   # Multi-process startup script
```

---

## ⚙️ Local Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ReRoute-AI.git
cd ReRoute-AI
```

### 2. Create & Activate a Virtual Environment

```bash
python -m venv venv

# On Windows:
.\venv\Scripts\Activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_GENAI_USE_VERTEXAI=True
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
MAPS_API_KEY=your_google_maps_api_key_here
```

---

## 🏃‍♂️ Running Locally (Dual Terminals)

**Terminal 1: start the FastAPI backend**

```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2: start the Streamlit frontend**

```bash
streamlit run frontend/app.py
```

---

## 🚢 Cloud Run Deployment

To build and deploy the containerized application to Google Cloud Run:

```bash
gcloud run deploy reroute-service \
  --source . \
  --region us-central1 \
  --project your-gcp-project-id \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=True,GOOGLE_CLOUD_PROJECT=your-gcp-project-id,GOOGLE_CLOUD_LOCATION=us-central1"
```

> The Maps API key should be stored in **Google Cloud Secret Manager** and attached to the service (for example with `--set-secrets`), not passed as a plain environment variable.

---

## 🔗 Live Links & Demo

- **Final Product Link (Cloud Run):** https://reroute-service-327909151923.us-central1.run.app/
- **Demo Video:** [Google Drive Demo Recording](ADD_YOUR_DRIVE_LINK_HERE)

---

## 🏆 Team DuoForge

Built for the AI Builder Cup.