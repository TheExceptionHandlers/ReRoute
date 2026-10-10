import math
import os
from google.cloud import firestore

if "GOOGLE_APPLICATION_CREDENTIALS" not in os.environ:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

db = firestore.Client(project="project-phoenix-ai-511013")

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Earth radius in miles
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

def match_artisan_and_arbitrage(customer_lat: float, customer_lon: float, required_skill: str, retail_price: float, estimated_repair: float) -> dict:
    artisans_ref = db.collection("artisans").stream()
    candidates = []

    for doc in artisans_ref:
        data = doc.to_dict()
        if data.get("active") and required_skill in data.get("skills", []):
            dist = calculate_haversine_distance(customer_lat, customer_lon, data["latitude"], data["longitude"])
            if dist <= 10.0:  # Within 10-mile catchment radius
                candidates.append((dist, data))

    # Match closest qualified artisan
    candidates.sort(key=lambda x: x[0])
    selected = candidates[0] if candidates else None

    # Economic & Scope-3 Carbon Arbitrage
    freight_shipping_cost = 6.80
    warehouse_processing = 7.50
    liquidation_markdown_loss = retail_price * 0.70
    status_quo_total_loss = freight_shipping_cost + warehouse_processing + liquidation_markdown_loss

    local_bounty = selected[1]["base_bounty_rate"] if selected else estimated_repair
    recommerce_value = retail_price * 0.75
    reroute_net_recovery = recommerce_value - local_bounty
    net_savings = reroute_net_recovery - (-status_quo_total_loss)

    # Ton-mile Scope 3 Freight vs Local drop-off CO2 (approx kg CO2)
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