from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.service_request import ServiceRequestCreate, ServiceRequestResponse, ServiceRequestListResponse
from app.application.service_request_service import ServiceRequestService
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowInstance

router = APIRouter()
_service = ServiceRequestService()

@router.get("", response_model=List[ServiceRequestListResponse])
@router.get("/", response_model=List[ServiceRequestListResponse], include_in_schema=False)
def list_requests(db: Session = Depends(get_db)):
    """List all service requests (applications) with their workflow IDs."""
    requests = db.query(ServiceRequest).order_by(ServiceRequest.created_at.desc()).limit(100).all()
    results = []
    for sr in requests:
        wf = db.query(WorkflowInstance).filter_by(service_request_id=sr.request_id).first()
        results.append(ServiceRequestListResponse(
            id=sr.id,
            request_id=sr.request_id,
            citizen_id=sr.citizen_id,
            service_type=sr.service_type,
            status=sr.status,
            created_at=sr.created_at,
            workflow_id=wf.workflow_id if wf else None,
        ))
    return results

@router.post("", response_model=ServiceRequestResponse)
@router.post("/", response_model=ServiceRequestResponse, include_in_schema=False)
async def create_service_request(
    payload: ServiceRequestCreate, request: Request, db: Session = Depends(get_db)
):
    return await ServiceRequestService().create(
        db=db,
        citizen_id=payload.citizen_id,
        service_type=payload.service_type.value,
        correlation_id=request.state.correlation_id,
    )
