import os
from google.cloud import firestore

# Point to your local service account credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "gcp-credentials.json"

# Initialize Firestore
db = firestore.Client(project="project-phoenix-ai-511013")

# Mock local repair artisans with distinct geocoded coordinates & skill profiles
artisans = [
    {
        "id": "artisan_01",
        "name": "Stitch & Save Atelier",
        "service_type": "textile_repair",
        "skills": ["zipper_replacement", "seam_restoration", "button_repair", "patching"],
        "latitude": 12.9352,   # Koramangala (~3.2 miles from city center 12.9716, 77.5946)
        "longitude": 77.6245,
        "base_bounty_rate": 8.50,
        "turnaround_hours": 24,
        "rating": 4.9,
        "active": True
    },
    {
        "id": "artisan_02",
        "name": "EcoSole Cobblers & Leatherworks",
        "service_type": "footwear_repair",
        "skills": ["sole_reglue", "leather_patching", "heel_repair", "stitching"],
        "latitude": 12.9784,   # Indiranagar (~2.8 miles from city center)
        "longitude": 77.6408,
        "base_bounty_rate": 12.00,
        "turnaround_hours": 48,
        "rating": 4.8,
        "active": True
    },
    {
        "id": "artisan_03",
        "name": "Revive Tailoring Lab",
        "service_type": "textile_repair",
        "skills": ["zipper_replacement", "lining_repair", "tear_mending"],
        "latitude": 13.0068,   # Malleshwaram (~3.1 miles from city center)
        "longitude": 77.5713,
        "base_bounty_rate": 7.00,
        "turnaround_hours": 12,
        "rating": 4.7,
        "active": True
    }
]

def seed_database():
    print("Connecting to Firestore and populating artisan registry...")
    for artisan in artisans:
        doc_ref = db.collection("artisans").document(artisan["id"])
        doc_ref.set(artisan)
        print(f"  [✓] Seeded: {artisan['name']} ({artisan['id']})")
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()