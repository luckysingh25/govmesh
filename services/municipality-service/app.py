import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

department = os.getenv("DEPARTMENT_NAME", "municipality")
app = FastAPI(title="GovMesh Municipality Service Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "municipality-service", "department": department}

@app.get("/records/{citizen_id}")
def get_record(citizen_id: str):
    return {
        "department": department,
        "service": "municipality-service",
        "citizen_id": citizen_id,
        "verified": True,
        "municipality_data": {
            "address": f"Building {citizen_id}, Main Street",
            "ward_number": "W-12",
            "water_clearance": True
        }
    }
