from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.agents.diagnostic import inspect_defect
from backend.agents.routing import match_artisan_and_arbitrage
from backend.agents.fraud_guard import verify_repair_receipt
from dotenv import load_dotenv
from pydantic import BaseModel
from backend.database import save_return_job
import uuid
import json

load_dotenv() 

app = FastAPI()

class BookingRequest(BaseModel):
    customer_name: str
    item_name: str
    defect: str
    artisan_id: str
    artisan_name: str
    workflow: str
    status: str

@app.post("/api/v1/book-service")
def book_service_endpoint(booking: BookingRequest):
    try:
        job_id = f"JOB-{uuid.uuid4().hex[:4].upper()}"
        job_data = booking.dict()
        save_return_job(job_id, job_data)
        return {"status": "success", "job_id": job_id}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

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

        job_id = f"JOB-{uuid.uuid4().hex[:4].upper()}"
        job_record = {
            "item": product_name,
            "retail_price": retail_price,
            "status": "Pending Drop-off / Pickup",
            "artisan_id": result.get("arbitrage", {}).get("artisan_matched", {}).get("id", "artisan_01"),
            "bounty": result.get("arbitrage", {}).get("net_savings_usd", 10.0) * 50 # Example INR mapping
        }
        save_return_job(job_id, job_record)
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