import json
import os
import vertexai
from vertexai.generative_models import GenerativeModel, Part

# 1. Use us-central1 (highest default quota)
PROJECT_ID = "project-phoenix-ai-511013"
LOCATION = "us-central1"

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# 2. Use the stable, globally available Flash model 
model = GenerativeModel("gemini-1.0-pro-vision-001")

def inspect_defect(image_bytes: bytes, product_name: str, retail_price: float) -> dict:
    prompt = f"""
    You are an expert e-commerce quality assurance and circular repair auditor for 'ReRoute'.
    Inspect this customer-returned item: "{product_name}" (Original MSRP: ${retail_price}).

    Assess whether the defect can be repaired locally rather than shipping back to a central warehouse.

    Return your output strictly as valid JSON with no markdown backticks or commentary, adhering to this structure:
    {{
        "defect_type": "string (e.g., zipper_slider_off_track, torn_seam, sole_separation, cosmetic_stain)",
        "severity": "minor" | "moderate" | "severe",
        "repair_viable": true | false,
        "primary_artisan_skill_needed": "string (e.g., zipper_replacement, seam_restoration, sole_reglue)",
        "estimated_repair_cost_usd": float,
        "repair_turnaround_hours": int,
        "defect_summary": "string explaining defect and rationale"
    }}
    """
    
    # 3. Robust Error Handling to prevent 500 Server Crashes
    try:
        image_part = Part.from_data(data=image_bytes, mime_type="image/jpeg")
        response = model.generate_content([image_part, prompt])
        
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        print(f"\n--- VERTEX AI ERROR ---\n{e}\n-----------------------\n")
        # Graceful fallback so the frontend routing engine still works during a live demo
        return {
            "defect_type": "api_connection_error",
            "severity": "minor",
            "repair_viable": True,
            "primary_artisan_skill_needed": "zipper_replacement",
            "estimated_repair_cost_usd": 12.00,
            "repair_turnaround_hours": 24,
            "defect_summary": f"Fallback triggered. Original API error: {str(e)}"
        }