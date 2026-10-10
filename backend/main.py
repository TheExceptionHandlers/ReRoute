from fastapi import FastAPI, UploadFile, File, Form
from backend.agents.diagnostic import inspect_defect
from backend.agents.routing import match_artisan_and_arbitrage

app = FastAPI(title="ReRoute Reverse-Triangulation Engine")

@app.get("/health")
def health():
    return {"status": "online", "system": "ReRoute"}

@app.post("/api/v1/intercept")
async def intercept_return(
    product_name: str = Form(...),
    retail_price: float = Form(...),
    customer_lat: float = Form(12.9716),
    customer_lon: float = Form(77.5946),
    file: UploadFile = File(...)
):
    image_bytes = await file.read()
    
    # 1. Run Multimodal Defect Analysis
    diagnosis = inspect_defect(image_bytes, product_name, retail_price)

    # 2. Run Geospatial Matching & Economic Arbitrage
    skill = diagnosis.get("primary_artisan_skill_needed", "zipper_replacement")
    est_cost = diagnosis.get("estimated_repair_cost_usd", 8.00)
    routing = match_artisan_and_arbitrage(customer_lat, customer_lon, skill, retail_price, est_cost)

    return {
        "diagnosis": diagnosis,
        "arbitrage": routing
    }