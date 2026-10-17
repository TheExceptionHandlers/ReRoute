from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.agents.diagnostic import inspect_defect
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
        
        # 1. Execute the unified ADK Agent
        print("\n🤖 [ADK 2.0] Initializing Agent Pipeline...", flush=True)
        
        # Pass all data, including coordinates, directly to the agent
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