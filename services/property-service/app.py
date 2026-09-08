import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

department = os.getenv("DEPARTMENT_NAME", "property")
app = FastAPI(title="GovMesh Property Service Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "property-service", "department": department}

@app.get("/records/{citizen_id}")
def get_record(citizen_id: str):
    return {
        "department": department,
        "service": "property-service",
        "citizen_id": citizen_id,
        "verified": True,
        "property_data": {
            "property_id": f"PROP-{citizen_id}",
            "zone": "Urban-A",
            "ownership_status": "Clear"
        }
    }
