import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

department = os.getenv("DEPARTMENT_NAME", "tax")
app = FastAPI(title="GovMesh Tax Service Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "tax-service", "department": department}

@app.get("/records/{citizen_id}")
def get_record(citizen_id: str):
    return {
        "department": department,
        "service": "tax-service",
        "citizen_id": citizen_id,
        "verified": True,
        "tax_data": {
            "pan_number": f"ABCDE{citizen_id[:4]}F",
            "tax_dues_pending": False,
            "financial_year": "2025-2026"
        }
    }
