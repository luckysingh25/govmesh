from typing import List
from pathlib import Path
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestResponse, ServiceRequestListResponse
from app.application.service_request_service import ServiceRequestService
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowInstance
from app.models.user import User
from app.core.auth import get_current_user, ensure_citizen_access
from app.core.service_types import WORKFLOW_DEFINITIONS

router = APIRouter()
_service = ServiceRequestService()

@router.get("", response_model=List[ServiceRequestListResponse])
@router.get("/", response_model=List[ServiceRequestListResponse], include_in_schema=False)
def list_requests(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all service requests (applications) with their workflow IDs."""
    query = db.query(ServiceRequest)
    if current_user.role == "citizen":
        if not current_user.citizen_id:
            return []
        query = query.filter(ServiceRequest.citizen_id == current_user.citizen_id)
    requests = query.order_by(ServiceRequest.created_at.desc()).limit(100).all()
    request_ids = [sr.request_id for sr in requests if sr.request_id]
    
    # Batch load workflows in a single query instead of N queries
    wf_map = {}
    if request_ids:
        workflows = db.query(WorkflowInstance).filter(WorkflowInstance.service_request_id.in_(request_ids)).all()
        for wf in workflows:
            if wf.service_request_id not in wf_map:
                wf_map[wf.service_request_id] = wf.workflow_id

    results = []
    for sr in requests:
        results.append(ServiceRequestListResponse(
            id=sr.id,
            request_id=sr.request_id,
            citizen_id=sr.citizen_id,
            service_type=sr.service_type,
            status=sr.status,
            created_at=sr.created_at,
            completed_at=sr.completed_at,
            duration_ms=(
                max(0, int((sr.completed_at - sr.created_at).total_seconds() * 1000))
                if sr.completed_at and sr.created_at
                else None
            ),
            workflow_id=wf_map.get(sr.request_id),
        ))
    return results

@router.post("", response_model=ServiceRequestResponse)
@router.post("/", response_model=ServiceRequestResponse, include_in_schema=False)
async def create_service_request(
    payload: ServiceRequestCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    ensure_citizen_access(current_user, payload.citizen_id)
    return await ServiceRequestService().create(
        db=db,
        citizen_id=payload.citizen_id,
        service_type=payload.service_type.value,
        correlation_id=request.state.correlation_id,
        actor=current_user.email,
    )


@router.get("/definitions")
def get_service_definitions(_current_user: User = Depends(get_current_user)):
    reasons = {
        "identity": "Verifies the authenticated fictional citizen's identity.",
        "property": "Checks synthetic ownership and property registry information.",
        "municipality": "Confirms synthetic municipal registration and address.",
        "tax": "Checks the synthetic tax clearance job and outstanding amount.",
    }
    return [
        {"id": name, "label": name.replace("_", " ").title(), "description": item["description"], "departments": [{"id": dept, "reason": reasons[dept]} for dept in item["steps"]]}
        for name, item in WORKFLOW_DEFINITIONS.items()
    ]


@router.get("/metrics")
def get_request_metrics(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    query = db.query(ServiceRequest).filter(ServiceRequest.created_at >= start)
    if current_user.role == "citizen":
        query = query.filter(ServiceRequest.citizen_id == current_user.citizen_id)
    rows = query.all()
    completed = [row for row in rows if row.status in {"success", "completed"}]
    durations = [(row.completed_at - row.created_at).total_seconds() * 1000 for row in completed if row.completed_at and row.created_at]
    return {
        "scope": "authenticated citizen" if current_user.role == "citizen" else "platform",
        "period": "today",
        "total_requests": len(rows),
        "completed_requests": len(completed),
        "completion_rate": round(len(completed) / len(rows) * 100) if rows else 0,
        "average_duration_ms": round(sum(durations) / len(durations)) if durations else None,
        "active_citizens": len({row.citizen_id for row in rows}),
    }


@router.get("/demo/scenarios")
def get_demo_scenarios(current_user: User = Depends(get_current_user)):
    path = Path(__file__).resolve().parents[4] / "services" / "seed" / "scenarios.json"
    rows = json.loads(path.read_text(encoding="utf-8"))
    service_by_scenario = {"tax_pending":"tax_clearance", "tax_due":"tax_clearance", "property_missing":"property_transfer"}
    for row in rows:
        row["service_type"] = service_by_scenario.get(row["scenario_name"], "business_registration")
        row["selectable"] = current_user.role != "citizen" or row["citizen_id"] == current_user.citizen_id
        row["fictional"] = True
    return rows
