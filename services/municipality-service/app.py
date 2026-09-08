from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Municipality Service (Simulated)")

class MunicipalityData(BaseModel):
    resident_name: str
    municipal_id: str
    ward: str
    address: str

MOCK_DB = {
    "CIT-1001": MunicipalityData(
        resident_name="Rajesh Kumar",
        municipal_id="MUN-BLR-045",
        ward="Ward 72 - Domlur",
        address="123 MG Road, Bangalore"
    ),
    "CIT-1002": MunicipalityData(
        resident_name="Priya Sharma",
        municipal_id="MUN-CCU-089",
        ward="Ward 45 - Park Street",
        address="456 Park Street, Kolkata"
    )
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "municipality"}

@app.get("/api/municipality/{citizen_id}")
def get_municipality(citizen_id: str, x_api_key: str = Header(None)):
    if x_api_key != "sim_municipality_key":
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    
    if citizen_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Resident not found")
        
    return MOCK_DB[citizen_id]
