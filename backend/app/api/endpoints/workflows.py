"""Workflow API endpoints.

Provides routes to start workflows, query status, and retrieve timelines.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.application.workflow_engine import WorkflowEngine
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowInstance, WorkflowStepInstance
from app.schemas.workflow import (
    WorkflowStartRequest,
    WorkflowStatusResponse,
    WorkflowStepStatus,
    WorkflowTimelineResponse,
    TimelineEntry,
)

logger = logging.getLogger(__name__)
router = APIRouter()
_engine = WorkflowEngine()


@router.post("/start", response_model=WorkflowStatusResponse)
async def start_workflow(payload: WorkflowStartRequest, db: Session = Depends(get_db)):
    """Manually start a workflow for an existing service request."""
    sr = db.query(ServiceRequest).filter_by(request_id=payload.service_request_id).first()
    if sr is None:
        raise HTTPException(status_code=404, detail="Service request not found")

    # Check if workflow already exists
    existing = db.query(WorkflowInstance).filter_by(service_request_id=sr.request_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Workflow already exists for this request")

    instance = _engine.start_workflow(
        db=db,
        service_request_id=sr.request_id,
        citizen_id=sr.citizen_id,
        definition_name="business_registration",
    )

    return _build_status_response(db, instance)


@router.get("/{workflow_id}", response_model=WorkflowStatusResponse)
def get_workflow_status(workflow_id: str, db: Session = Depends(get_db)):
    """Retrieve workflow status with all step statuses."""
    instance = db.query(WorkflowInstance).filter_by(workflow_id=workflow_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _build_status_response(db, instance)


@router.get("/{workflow_id}/timeline", response_model=WorkflowTimelineResponse)
def get_workflow_timeline(workflow_id: str, db: Session = Depends(get_db)):
    """Retrieve the ordered timeline of steps for a workflow."""
    instance = db.query(WorkflowInstance).filter_by(workflow_id=workflow_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Workflow not found")

    entries = []
    for step in instance.steps:
        duration_ms = None
        if step.started_at and step.completed_at:
            duration_ms = int((step.completed_at - step.started_at).total_seconds() * 1000)
        entries.append(TimelineEntry(
            step_name=step.step_name,
            step_index=step.step_index,
            status=step.status,
            attempt_count=step.attempt_count,
            max_retries=step.max_retries,
            error_message=step.error_message,
            started_at=step.started_at,
            completed_at=step.completed_at,
            duration_ms=duration_ms,
        ))

    return WorkflowTimelineResponse(
        workflow_id=instance.workflow_id,
        service_request_id=instance.service_request_id,
        overall_status=instance.status,
        created_at=instance.created_at,
        timeline=entries,
    )


@router.get("/by-request/{request_id}", response_model=WorkflowStatusResponse)
def get_workflow_by_request(request_id: str, db: Session = Depends(get_db)):
    """Look up a workflow by its parent service-request ID."""
    instance = db.query(WorkflowInstance).filter_by(service_request_id=request_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="No workflow found for this request")
    return _build_status_response(db, instance)


# ── Helpers ───────────────────────────────────────────────────────────

def _build_status_response(db: Session, instance: WorkflowInstance) -> WorkflowStatusResponse:
    """Build a WorkflowStatusResponse from an ORM instance."""
    step_statuses = []
    for step in instance.steps:
        duration_ms = None
        if step.started_at and step.completed_at:
            duration_ms = int((step.completed_at - step.started_at).total_seconds() * 1000)
        step_statuses.append(WorkflowStepStatus(
            step_name=step.step_name,
            step_index=step.step_index,
            status=step.status,
            attempt_count=step.attempt_count,
            max_retries=step.max_retries,
            result_data=step.result_data,
            error_message=step.error_message,
            started_at=step.started_at,
            completed_at=step.completed_at,
            next_retry_at=step.next_retry_at,
            duration_ms=duration_ms,
        ))

    return WorkflowStatusResponse(
        workflow_id=instance.workflow_id,
        service_request_id=instance.service_request_id,
        citizen_id=instance.citizen_id,
        definition_name=instance.definition.name,
        status=instance.status,
        current_step_index=instance.current_step_index,
        steps=step_statuses,
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        completed_at=instance.completed_at,
    )
