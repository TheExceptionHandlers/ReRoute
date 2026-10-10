import json
import os
import google.generativeai as genai

# Keep this so your Firestore database doesn't break!
if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

# Bypass Vertex AI and use the instant Developer API
genai.configure(api_key="AQ.Ab8RN6JRs5qa1m4QgxJSpVSdWn-lAde5jjpHES2KevAeW4UElQ")

# Explicitly use the newest model as required by the API
model = genai.GenerativeModel("gemini-3.8-flash")

def inspect_defect(image_bytes: bytes, product_name: str, retail_price: float) -> dict:
    prompt = f"""
    You are an expert e-commerce quality assurance and circular repair auditor for 'ReRoute'.
    Inspect this customer-returned item: "{product_name}" (Original MSRP: ${retail_price}).

    Assess whether the defect can be repaired locally rather than shipping back to a central warehouse.

    Return your output strictly as valid JSON with no markdown backticks or commentary, adhering to this structure:
    {{
        "defect_type": "string (e.g., zipper_slider_off_track, torn_seam, sole_separation)",
        "severity": "minor" | "moderate" | "severe",
        "repair_viable": true | false,
        "primary_artisan_skill_needed": "string (e.g., zipper_replacement, seam_restoration)",
        "estimated_repair_cost_usd": float,
        "repair_turnaround_hours": int,
        "defect_summary": "string explaining defect and rationale"
    }}
    """
    
    try:
        # AI Studio format for images
        image_part = {
            "mime_type": "image/jpeg",
            "data": image_bytes
        }
        
        response = model.generate_content([image_part, prompt])
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
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