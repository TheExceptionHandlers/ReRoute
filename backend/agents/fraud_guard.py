import os
import json
import asyncio
from google.adk.agents import Agent
from google.adk.runners import InMemoryRunner
from google.genai import types

def verify_repair_receipt(image_bytes: bytes, estimated_cost: float):
    fraud_agent = Agent(
        name="ReRoute_Fraud_Guard",
        model="gemini-2.5-flash",
        instruction=f"""
        You are an enterprise fraud detection agent for a reverse logistics platform.
        Step 1: Extract the total amount paid from the uploaded repair receipt image.
        Step 2: Compare it to the AI's estimated repair cost of ₹{estimated_cost}.
        Step 3: If the receipt total is within a 20% variance of the estimate, mark status as "VERIFIED".
        Step 4: If the amount is drastically higher, or if the image is clearly not a receipt, mark status as "FLAGGED".
        
        Return ONLY raw JSON with no markdown blocks:
        {{
            "extracted_amount_inr": float,
            "status": "VERIFIED" | "FLAGGED",
            "reason": "string explaining the decision"
        }}
        """,
        tools=[]
    )
    
    runner = InMemoryRunner(agent=fraud_agent, app_name="fraud_app")
    
    async def run_fraud_check():
        session = await runner.session_service.create_session(app_name="fraud_app", user_id="admin")
        content = types.Content(
            role="user", 
            parts=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                types.Part.from_text(text="Verify this receipt against the estimate.")
            ]
        )
        final_text = ""
        async for event in runner.run_async(user_id="admin", session_id=session.id, new_message=content):
            if hasattr(event, 'content') and getattr(event.content, 'parts', None):
                for part in event.content.parts:
                    if part.text: final_text = part.text
        return final_text
        
    try:
        response_text = asyncio.run(run_fraud_check())
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json\n", "").replace("```", "")
        return json.loads(response_text)
    except Exception as e:
        return {"error": str(e), "status": "ERROR"}