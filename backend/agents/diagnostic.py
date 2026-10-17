import os
import json
import asyncio

# 1. The exact flags required by ADK 2.0 to trigger Vertex AI authentication
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
os.environ["GOOGLE_CLOUD_PROJECT"] = "project-phoenix-ai-511013"
os.environ["GOOGLE_CLOUD_LOCATION"] = "us-central1"

from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types
from backend.agents.routing import match_artisan_and_arbitrage

def inspect_defect(image_bytes: bytes, product_name: str, retail_price: float, lat: float, lon: float):
    # 2. Instantiate the ADK Managed Agent
    diagnostic_agent = Agent(
        name="ReRoute_Diagnostic_Agent",
        model="gemini-2.5-flash", 
        instruction="""
        You are a reverse logistics diagnostic agent.
        Step 1: Analyze the uploaded image to identify the defect type and severity.
        Step 2: Estimate the local repair cost in USD.
        Step 3: Call the 'match_artisan_and_arbitrage' tool using the customer's coordinates, your estimated repair cost, the product's retail price, and the defect type.
        Step 4: Return a strict JSON response containing the final defect analysis and the arbitrage results from the tool.
        
        Do not format with markdown blocks like ```json. Return raw JSON only.
        
        Required JSON structure:
        {
          "diagnosis": {
              "defect_type": "string",
              "severity": "minor | moderate | severe",
              "estimated_repair_cost_usd": float,
              "repair_turnaround_hours": int,
              "defect_summary": "string"
          },
          "arbitrage": { ... results from the tool ... }
        }
        """,
        tools=[match_artisan_and_arbitrage]
    )
    
    # 3. Attach the Agent to an ADK Runner
    runner = InMemoryRunner(agent=diagnostic_agent, app_name="reroute_app")
    
    # 4. ADK runs on an event loop; we wrap it in an async function
    async def run_adk_swarm():
        session = await runner.session_service.create_session(
            app_name="reroute_app", 
            user_id="customer"
        )
        
        prompt = f"Analyze this {product_name} (MSRP: ${retail_price}) at coordinates {lat}, {lon}."
        content = types.Content(
            role="user", 
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part.from_text(text=prompt)
            ]
        )
        
        final_text = ""
        
        async for event in runner.run_async(
            user_id="customer", 
            session_id=session.id, 
            new_message=content
        ):
            if hasattr(event, 'content') and getattr(event.content, 'parts', None):
                for part in event.content.parts:
                    if part.text:
                        final_text = part.text
                        
        return final_text

    print("\n--- [ADK 2.0] Dispatching Agent Swarm ---", flush=True)
    
    try:
        # 5. Bridge the async ADK runner back to your synchronous FastAPI endpoint
        response_text = asyncio.run(run_adk_swarm())
        print(f"--- [ADK 2.0] Agent Execution Complete ---\nRaw Output: {response_text}", flush=True)
        
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json\n", "").replace("```", "")
            
        data = json.loads(response_text)
        return data
        
    except Exception as e:
        print(f"--- [ADK 2.0] Execution Failed: {e}", flush=True)
        return {"error": f"Agent Run Failed: {str(e)}"}