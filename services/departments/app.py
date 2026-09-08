import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

department = os.getenv("DEPARTMENT_NAME", "department")
app = FastAPI(title=f"GovMesh {department.title()} Simulator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "department": department}


@app.get("/records/{citizen_id}")
def get_record(citizen_id: str):
    """Safe mock response used to demonstrate cross-department calls at the hackathon."""
    return {
        "department": department,
        "citizen_id": citizen_id,
        "verified": True,
        "message": f"Mock {department} record found",
    }
