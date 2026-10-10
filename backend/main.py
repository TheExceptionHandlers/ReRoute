from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from backend.agents.diagnostic import inspect_defect
from backend.agents.routing import match_artisan_and_arbitrage

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
        print("\n--- NEW REQUEST INTERCEPTED ---")
        image_bytes = file.file.read()
        
        # 1. Manually close the file I/O to prevent Starlette background task hanging
        file.file.close() 
        
        print("-> 1. Running Diagnostic Agent...")
        diagnosis = inspect_defect(image_bytes, product_name, retail_price)
        
        print("-> 2. Running Routing Agent...")
        defect = diagnosis.get("defect_type", "unknown_defect") if isinstance(diagnosis, dict) else "unknown_defect"
        
        # Ensure we are passing clean python floats, not accidental strings/NaNs
        repair_cost = float(diagnosis.get("estimated_repair_cost_usd", 15.0) if isinstance(diagnosis, dict) else 15.0)
        retail_price_clean = float(retail_price)
        
        arbitrage = match_artisan_and_arbitrage(customer_lat, customer_lon, defect, retail_price_clean, repair_cost)
        
        print("-> 3. Protocol Complete! Forcing JSON dump to UI...")
        
        # 2. Bypass FastAPI's auto-encoder and return a strict JSONResponse
        return JSONResponse(
            status_code=200,
            content={
                "diagnosis": diagnosis, 
                "arbitrage": arbitrage
            }
        )
        
    except Exception as e:
        print(f"CRITICAL BACKEND ERROR: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": str(e)}
        )