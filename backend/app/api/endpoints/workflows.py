"""Workflow API endpoints.

Provides routes to start workflows, query status, and retrieve timelines.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.application.workflow_engine import WorkflowEngine
from app.application.policy_service import PolicyService
from app.connectors.base import ConnectorResult
from app.core.auth import get_current_user, ensure_citizen_access
from app.core.service_types import KNOWN_DEPARTMENTS
from app.intelligence import generate_insights
from app.models.user import User
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
async def start_workflow(payload: WorkflowStartRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Manually start a workflow for an existing service request."""
    sr = db.query(ServiceRequest).filter_by(request_id=payload.service_request_id).first()
    if sr is None:
        raise HTTPException(status_code=404, detail="Service request not found")
    ensure_citizen_access(current_user, sr.citizen_id)
    policy = PolicyService().evaluate(db, sr.citizen_id, sr.service_type, sr.correlation_id)
    if policy.decision != "allow" or sr.status == "denied":
        raise HTTPException(status_code=403, detail="Current consent does not authorize workflow execution")

    # Check if workflow already exists
    existing = db.query(WorkflowInstance).filter_by(service_request_id=sr.request_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Workflow already exists for this request")

    instance = _engine.start_workflow(
        db=db,
        service_request_id=sr.request_id,
        citizen_id=sr.citizen_id,
        definition_name=sr.service_type,
    )
    await _engine.execute_workflow_sync(db, instance.id)
    db.refresh(instance)

    return _build_status_response(db, instance)


@router.post("/by-request/{request_id}/resume", response_model=WorkflowStatusResponse)
async def resume_workflow(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sr = db.query(ServiceRequest).filter_by(request_id=request_id).first()
    if sr is None:
        raise HTTPException(status_code=404, detail="Service request not found")
    ensure_citizen_access(current_user, sr.citizen_id)
    policy = PolicyService().evaluate(db, sr.citizen_id, sr.service_type, sr.correlation_id)
    if policy.decision != "allow":
        raise HTTPException(status_code=403, detail="Current consent does not authorize resume")
    instance = db.query(WorkflowInstance).filter_by(service_request_id=request_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="No workflow found for this request")
    await _engine.resume_or_retry(db, instance)
    return _build_status_response(db, instance)


@router.get("/{workflow_id}", response_model=WorkflowStatusResponse)
def get_workflow_status(workflow_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve workflow status with all step statuses."""
    instance = db.query(WorkflowInstance).filter_by(workflow_id=workflow_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    ensure_citizen_access(current_user, instance.citizen_id)
    return _build_status_response(db, instance)


@router.get("/{workflow_id}/timeline", response_model=WorkflowTimelineResponse)
def get_workflow_timeline(workflow_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve the ordered timeline of steps for a workflow."""
    instance = db.query(WorkflowInstance).filter_by(workflow_id=workflow_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    ensure_citizen_access(current_user, instance.citizen_id)

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
def get_workflow_by_request(request_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Look up a workflow by its parent service-request ID."""
    instance = db.query(WorkflowInstance).filter_by(service_request_id=request_id).first()
    if instance is None:
        raise HTTPException(status_code=404, detail="No workflow found for this request")
    ensure_citizen_access(current_user, instance.citizen_id)
    return _build_status_response(db, instance)


# ── Helpers ───────────────────────────────────────────────────────────

def _build_status_response(db: Session, instance: WorkflowInstance) -> WorkflowStatusResponse:
    """Build a WorkflowStatusResponse from an ORM instance."""
    step_statuses = []
    for step in instance.steps:
        duration_ms = step.duration_ms
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
            protocol=step.protocol,
            raw_response=step.raw_response,
            source_mapping=step.source_mapping,
            normalized_output=step.normalized_output,
            correlation_id=step.correlation_id,
            schema_version=step.schema_version,
            mapping_version=step.mapping_version,
            external_job_id=step.external_job_id,
        ))

    steps_by_name = {step.step_name: step for step in instance.steps}
    insight_inputs = []
    for department in KNOWN_DEPARTMENTS:
        step = steps_by_name.get(department)
        insight_inputs.append(ConnectorResult(
            department=department,
            status=step.status if step else "not_required",
            data=(step.result_data or {}) if step else {},
            error=step.error_message if step else None,
        ))
    insights = generate_insights(insight_inputs)

    return WorkflowStatusResponse(
        workflow_id=instance.workflow_id,
        service_request_id=instance.service_request_id,
        citizen_id=instance.citizen_id,
        definition_name=instance.definition.name,
        status=instance.status,
        current_step_index=instance.current_step_index,
        steps=step_statuses,
        insights=[insight.model_dump() for insight in insights],
        created_at=instance.created_at,
        updated_at=instance.updated_at,
        completed_at=instance.completed_at,
    )
