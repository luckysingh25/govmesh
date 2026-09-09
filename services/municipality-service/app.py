from pathlib import Path
import sys
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Response
from pydantic import BaseModel

SERVICES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICES_ROOT))
from seed_loader import load_seed_records  # noqa: E402

app = FastAPI(title="Municipality Service (Simulated)")


class MunicipalityData(BaseModel):
    citizen_id: str
    resident_name: str
    municipal_id: str
    ward: str
    address: str
    registration_status: Literal["ACTIVE", "INACTIVE"]


RECORDS = load_seed_records(
    SERVICES_ROOT / "seed" / "municipality.json", MunicipalityData
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "municipality"}


@app.get("/api/municipality/{citizen_id}", response_model=MunicipalityData)
def get_municipality(citizen_id: str, response: Response, x_api_key: str | None = Header(None), x_correlation_id: str | None = Header(None)):
    if x_api_key != "sim_municipality_key":
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    if x_correlation_id:
        response.headers["X-Correlation-ID"] = x_correlation_id
    record = RECORDS.get(citizen_id.upper())
    if record is None:
        raise HTTPException(status_code=404, detail="Resident not found")
    return record
