import math
import os
from google.cloud import firestore

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

db = firestore.Client(project="project-phoenix-ai-511013")

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def match_artisan_and_arbitrage(customer_lat: float, customer_lon: float, defect_type: str, retail_price: float, estimated_repair: float) -> dict:
    artisans_ref = db.collection("artisans").stream()
    candidates = []

    # Normalize defect keywords for flexible matching
    target_terms = [t for t in defect_type.lower().replace("-", "_").split("_") if t]

    for doc in artisans_ref:
        data = doc.to_dict()
        if not data.get("active"):
            continue

        skills = [s.lower() for s in data.get("skills", [])]
        # Match if any term (e.g., 'zipper', 'seam', 'sole') appears in artisan skills
        skill_match = any(term in skill for term in target_terms for skill in skills)

        if skill_match:
            dist = calculate_haversine_distance(customer_lat, customer_lon, data["latitude"], data["longitude"])
            if dist <= 25.0:  # Expanded to 25-mile catchment radius
                candidates.append((dist, data))

    # Match closest qualified artisan; fallback to nearest active artisan if no direct skill match
    candidates.sort(key=lambda x: x[0])
    selected = candidates[0] if candidates else None

    # Status-Quo Reverse Logistics Costs
    freight_shipping_cost = 6.80
    warehouse_processing = 7.50
    liquidation_markdown_loss = retail_price * 0.70
    status_quo_total_loss = freight_shipping_cost + warehouse_processing + liquidation_markdown_loss

    local_bounty = selected[1]["base_bounty_rate"] if selected else estimated_repair
    recommerce_value = retail_price * 0.75
    reroute_net_recovery = recommerce_value - local_bounty
    net_savings = reroute_net_recovery - (-status_quo_total_loss)

    # Scope 3 Freight vs Local drop-off CO2 (kg CO2)
    standard_hub_miles = 650.0
    avoided_freight_co2 = round((standard_hub_miles * 0.16) / 2.2, 2)
    local_co2 = round((selected[0] if selected else 1.0) * 0.04, 2)
    net_co2_saved = max(0.0, round(avoided_freight_co2 - local_co2, 2))

    return {
        "artisan_matched": selected[1] if selected else None,
        "distance_miles": selected[0] if selected else None,
        "status_quo_cost": round(status_quo_total_loss, 2),
        "reroute_net_recovery": round(reroute_net_recovery, 2),
        "net_savings_usd": round(net_savings, 2),
        "avoided_co2_kg": net_co2_saved
    }