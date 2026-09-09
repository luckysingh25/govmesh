from pathlib import Path
import sys
from typing import Literal

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel

SERVICES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICES_ROOT))
from seed_loader import load_seed_records  # noqa: E402

app = FastAPI(title="Identity Service (Simulated)")


class IdentityData(BaseModel):
    citizen_id: str
    full_name: str
    date_of_birth: str
    address: str
    verification_status: Literal["VERIFIED", "INCOMPLETE"]


RECORDS = load_seed_records(SERVICES_ROOT / "seed" / "identity.json", IdentityData)


@app.get("/health")
def health():
    return {"status": "ok", "service": "identity"}


@app.get("/api/identity/{citizen_id}", response_model=IdentityData)
def get_identity(citizen_id: str, authorization: str | None = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    record = RECORDS.get(citizen_id.upper())
    if record is None:
        raise HTTPException(status_code=404, detail="Citizen not found")
    return record

