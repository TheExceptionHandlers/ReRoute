import json
import os
from google import genai
from google.genai import types

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

# Delete the dummy string and paste your REAL Gemini API key!
client = genai.Client(api_key="AQ.Ab8RN6KG-7k-goMrlDN3ZurbXYdnvhYAYqNrtzv1gstXw3UhTw")

def inspect_defect(image_bytes: bytes, product_name: str, retail_price: float) -> dict:
    if not image_bytes:
        raise ValueError("Image bytes are empty! The backend received a 0-byte file.")

    prompt = f"""
    You are an expert e-commerce quality assurance and circular repair auditor for 'ReRoute'.
    Inspect this customer-returned item: "{product_name}" (Original MSRP: ${retail_price}).
    Assess whether the defect can be repaired locally rather than shipping back to a central warehouse.

    Return EXACTLY this JSON structure and nothing else:
    {{
        "defect_type": "zipper_separation",
        "severity": "minor",
        "repair_viable": true,
        "primary_artisan_skill_needed": "zipper_replacement",
        "estimated_repair_cost_usd": 15.00,
        "repair_turnaround_hours": 24,
        "defect_summary": "Brief explanation of the defect"
    }}
    """
    
    try:
        print(f"-> [1/3] Packaging image bytes... (Size: {len(image_bytes)} bytes)")
        
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )
        
        print("-> [2/3] Sending to Gemini API (Strict JSON Mode)...")
        
        # Enforcing JSON mode directly in the config prevents 504 Deadlines caused by formatting loops
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=[image_part, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        print("-> [3/3] Gemini response received!")
        return json.loads(response.text)
        
    except Exception as e:
        print(f"\n--- AI STUDIO ERROR ---\n{e}\n-----------------------\n")
        return {
            "defect_type": "api_connection_error",
            "severity": "minor",
            "repair_viable": True,
            "primary_artisan_skill_needed": "zipper_replacement",
            "estimated_repair_cost_usd": 12.00,
            "repair_turnaround_hours": 24,
            "defect_summary": f"Fallback triggered. Original API error: {str(e)}"
        }