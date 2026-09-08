import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

department = os.getenv("DEPARTMENT_NAME", "identity")
app = FastAPI(title="GovMesh Identity Service Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "identity-service", "department": department}

@app.get("/records/{citizen_id}")
def get_record(citizen_id: str):
    return {
        "department": department,
        "service": "identity-service",
        "citizen_id": citizen_id,
        "verified": True,
        "identity_data": {
            "name": f"Citizen {citizen_id}",
            "status": "Active",
            "national_id": f"ID-{citizen_id}"
        }
    }
