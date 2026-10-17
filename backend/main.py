from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.agents.diagnostic import inspect_defect
from backend.agents.routing import match_artisan_and_arbitrage
from backend.agents.fraud_guard import verify_repair_receipt
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
        image_bytes = file.file.read()
        file.file.close() 
        
        print("\n🤖 [ADK 2.0] Initializing Agent Pipeline...", flush=True)
        result = inspect_defect(
            image_bytes=image_bytes, 
            product_name=product_name, 
            retail_price=float(retail_price),
            lat=float(customer_lat),
            lon=float(customer_lon)
        )
        
        print("\n✅ [MISSION COMPLETE] Emitting unified payload to Streamlit UI", flush=True)
        print("="*50 + "\n", flush=True)
        return JSONResponse(status_code=200, content=result)
        
    except Exception as e:
        print(f"\n❌ [CRITICAL BACKEND ERROR]: {str(e)}", flush=True)
        return JSONResponse(status_code=500, content={"error": str(e)})
        

# --- NEW ENDPOINT FOR FRAUD GUARD ---
@app.post("/api/v1/verify-receipt")
def verify_receipt_endpoint(
    file: UploadFile = File(...),
    estimated_cost: float = Form(...)
):
    try:
        print("\n🧾 [FRAUD GUARD] Receipt Verification Triggered...", flush=True)
        image_bytes = file.file.read()
        file.file.close()
        
        result = verify_repair_receipt(image_bytes, estimated_cost)
        print(f"   • Result: {json.dumps(result)}", flush=True)
        return JSONResponse(status_code=200, content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})