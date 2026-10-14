import vertexai
from vertexai.generative_models import GenerativeModel, Part, GenerationConfig
import json

def inspect_defect(image_bytes: bytes, product_name: str, retail_price: float):
    vertexai.init(project="project-phoenix-ai-511013", location="us-central1")
    model = GenerativeModel("gemini-2.5-flash")
    
    image_part = Part.from_data(mime_type="image/jpeg", data=image_bytes)
    
    prompt = f"""
    You are an expert reverse logistics diagnostic agent.
    Analyze the uploaded image of {product_name} (MSRP: ${retail_price}).
    Return a strict JSON object with these exact keys:
    {{
      "defect_type": "string describing defect (e.g., torn_seam, broken_zipper, sole_separation)",
      "severity": "minor | moderate | severe",
      "estimated_repair_cost_usd": float,
      "repair_turnaround_hours": int,
      "defect_summary": "detailed description of the damage"
    }}
    """
    
    generation_config = GenerationConfig(
        response_mime_type="application/json",
        temperature=0.1
    )
    
    print("\n--- [DIAGNOSTIC] Dispatching to Vertex AI ---", flush=True)
    response = model.generate_content([image_part, prompt], generation_config=generation_config)
    
    print(f"--- [DIAGNOSTIC] Raw Vertex AI Response ---\n{response.text}\n-------------------------------------------", flush=True)
    
    try:
        data = json.loads(response.text)
        print(f"--- [DIAGNOSTIC] Successfully Parsed JSON: {data}", flush=True)
        return data
    except Exception as e:
        print(f"--- [DIAGNOSTIC] JSON Parsing Failed: {e}", flush=True)
        return {
            "defect_type": "unknown_defect",
            "estimated_repair_cost_usd": 15.0,
            "severity": "unknown",
            "repair_turnaround_hours": 24,
            "defect_summary": f"Raw output parsing failed: {response.text[:100]}"
        }