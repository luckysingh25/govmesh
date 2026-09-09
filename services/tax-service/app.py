from pathlib import Path
import sys
from typing import Literal

from fastapi import FastAPI, HTTPException, Header, Response
from pydantic import BaseModel

SERVICES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICES_ROOT))
from seed_loader import load_seed_records  # noqa: E402

app = FastAPI(title="Tax Service (Simulated)")


class TaxData(BaseModel):
    citizenId: str
    taxpayerName: str
    taxId: str
    taxStatus: Literal["CLEARED", "DUE", "PENDING"]
    outstandingAmount: float
    assessmentYear: str


RECORDS = load_seed_records(
    SERVICES_ROOT / "seed" / "tax.json", TaxData, id_field="citizenId"
)
JOB_POLLS: dict[str, int] = {}


@app.get("/health")
def health():
    return {"status": "ok", "service": "tax"}


@app.get("/api/tax/{citizen_id}", response_model=TaxData)
def get_tax(citizen_id: str):
    record = RECORDS.get(citizen_id.upper())
    if record is None:
        raise HTTPException(status_code=404, detail="Taxpayer not found")
    return record


@app.post("/api/tax/requests/{citizen_id}")
def submit_tax_lookup(citizen_id: str, response: Response, x_correlation_id: str | None = Header(None)):
    record = RECORDS.get(citizen_id.upper())
    if record is None:
        raise HTTPException(status_code=404, detail="Taxpayer not found")
    job_id = f"TAX-JOB-{record.citizenId}"
    if x_correlation_id:
        response.headers["X-Correlation-ID"] = x_correlation_id
    if record.taxStatus == "PENDING":
        JOB_POLLS.setdefault(job_id, 0)
        return {"job_id": job_id, "status": "pending"}
    return {"job_id": job_id, "status": "completed"}


@app.get("/api/tax/requests/{job_id}")
def get_tax_lookup(job_id: str, response: Response, x_correlation_id: str | None = Header(None)):
    citizen_id = job_id.removeprefix("TAX-JOB-").upper()
    record = RECORDS.get(citizen_id)
    if record is None or job_id != f"TAX-JOB-{citizen_id}":
        raise HTTPException(status_code=404, detail="Tax lookup not found")
    if x_correlation_id:
        response.headers["X-Correlation-ID"] = x_correlation_id
    if record.taxStatus == "PENDING":
        poll = JOB_POLLS.get(job_id, 0) + 1
        JOB_POLLS[job_id] = poll
        if poll == 1:
            return {"job_id": job_id, "status": "processing", "result": None}
        completed = record.model_copy(update={"taxStatus": "CLEARED", "outstandingAmount": 0.0})
        return {"job_id": job_id, "status": "completed", "result": completed}
    return {"job_id": job_id, "status": "completed", "result": record}
