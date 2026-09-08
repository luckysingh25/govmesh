from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Identity Service (Simulated)")

class IdentityData(BaseModel):
    citizen_id: str
    full_name: str
    date_of_birth: str
    address: str

MOCK_DB = {
    "CIT-1001": IdentityData(
        citizen_id="CIT-1001",
        full_name="Rajesh Kumar",
        date_of_birth="1985-06-15",
        address="123 MG Road, Bangalore, Karnataka"
    ),
    "CIT-1002": IdentityData(
        citizen_id="CIT-1002",
        full_name="Priya Sharma",
        date_of_birth="1990-11-20",
        address="456 Park Street, Kolkata, West Bengal"
    )
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "identity"}

@app.get("/api/identity/{citizen_id}")
def get_identity(citizen_id: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    if citizen_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Citizen not found")
        
    return MOCK_DB[citizen_id]
