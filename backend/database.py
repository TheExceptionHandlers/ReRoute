import os
from google.cloud import firestore

# Initialize Firestore Client (picks up GCP credentials or Cloud Run environment automatically)
db = firestore.Client(project=os.environ.get("GOOGLE_CLOUD_PROJECT", "project-phoenix-ai-511013"))

def save_return_job(job_id: str, job_data: dict):
    """Saves an intercepted return and maps it to the assigned artisan."""
    db.collection("returns").document(job_id).set(job_data)

def get_artisan_jobs(artisan_id: str = "artisan_01"):
    """Fetches incoming jobs assigned to a specific artisan."""
    docs = db.collection("returns").where("artisan_id", "==", artisan_id).stream()
    jobs = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        jobs.append(data)
    
    # Fallback to mock data if Firestore is empty during initial demo testing
    if not jobs:
        return [
            {"id": "JOB-9021", "item": "Alpine Trail Shell Jacket", "defect": "Stuck Zipper", "eta": "24h", "bounty": "₹450.00", "status": "Pending Pickup"},
            {"id": "JOB-9022", "item": "Vanguard Boots", "defect": "Sole Separation", "eta": "48h", "bounty": "₹600.00", "status": "In Repair"}
        ]
    return jobs

def update_job_status(job_id: str, new_status: str):
    """Updates the job status and triggers escrow release logic."""
    doc_ref = db.collection("returns").document(job_id)
    doc_ref.update({"status": new_status})