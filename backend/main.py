from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.agents.diagnostic import inspect_defect
from backend.agents.routing import match_artisan_and_arbitrage
import json

app = FastAPI()

@app.post("/api/v1/intercept")
def intercept_return(
    file: UploadFile = File(...),
    product_name: str = Form(...),
    retail_price: float = Form(...),
    customer_lat: float = Form(...),
    customer_lon: float = Form(...)
):
    try:
        print("\n" + "="*50, flush=True)
        print("📥 [SWARM INTAKE] New Return Intercepted", flush=True)
        print(f"   • Product: {product_name} (${retail_price})", flush=True)
        print(f"   • Location: {customer_lat}, {customer_lon}", flush=True)
        
        image_bytes = file.file.read()
        file.file.close() 
        print(f"   • Image Received: {file.filename} ({len(image_bytes)} bytes)", flush=True)
        
        print("\n🤖 [AGENT 1: DIAGNOSTIC] Dispatching to Gemini Vision...", flush=True)
        diagnosis = inspect_defect(image_bytes, product_name, retail_price)
        print(f"   • Raw Diagnosis Result: {json.dumps(diagnosis, indent=2)}", flush=True)
        
        defect = diagnosis.get("defect_type", "unknown_defect") if isinstance(diagnosis, dict) else "unknown_defect"
        repair_cost = float(diagnosis.get("estimated_repair_cost_usd", 15.0) if isinstance(diagnosis, dict) else 15.0)
        retail_price_clean = float(retail_price)
        
        print(f"\n🗺️ [AGENT 2: ROUTING] Triangulating artisans for defect: '{defect}'...", flush=True)
        arbitrage = match_artisan_and_arbitrage(customer_lat, customer_lon, defect, retail_price_clean, repair_cost)
        print(f"   • Arbitrage Computed: {json.dumps(arbitrage, indent=2)}", flush=True)
        
        print("\n✅ [MISSION COMPLETE] Emitting unified payload to Streamlit UI", flush=True)
        print("="*50 + "\n", flush=True)
        
        return JSONResponse(status_code=200, content={"diagnosis": diagnosis, "arbitrage": arbitrage})
        
    except Exception as e:
        print(f"\n❌ [CRITICAL BACKEND ERROR]: {str(e)}", flush=True)
        return JSONResponse(status_code=500, content={"error": str(e)})