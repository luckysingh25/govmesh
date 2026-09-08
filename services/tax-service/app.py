from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Tax Service (Simulated)")

class TaxData(BaseModel):
    taxpayerName: str
    taxId: str
    taxStatus: str
    outstandingAmount: float

MOCK_DB = {
    "CIT-1001": TaxData(
        taxpayerName="Rajesh Kumar",
        taxId="PAN-AXXXX1234Z",
        taxStatus="CLEARED",
        outstandingAmount=0.0
    ),
    "CIT-1002": TaxData(
        taxpayerName="Priya Sharma",
        taxId="PAN-BXXXX5678Y",
        taxStatus="DUE",
        outstandingAmount=14500.50
    )
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "tax"}

@app.get("/api/tax/{citizen_id}")
def get_tax(citizen_id: str):
    if citizen_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Taxpayer not found")
        
    return MOCK_DB[citizen_id]


# A deliberately small legacy/asynchronous-style facade: the consumer submits a
# lookup and then reads the completed job. Jobs are deterministic for the demo.
@app.post("/api/tax/requests/{citizen_id}")
def submit_tax_lookup(citizen_id: str):
    if citizen_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Taxpayer not found")
    return {"job_id": f"TAX-JOB-{citizen_id}", "status": "completed"}


@app.get("/api/tax/requests/{job_id}")
def get_tax_lookup(job_id: str):
    citizen_id = job_id.removeprefix("TAX-JOB-")
    if citizen_id not in MOCK_DB:
        raise HTTPException(status_code=404, detail="Tax lookup not found")
    return {"job_id": job_id, "status": "completed", "result": MOCK_DB[citizen_id]}
