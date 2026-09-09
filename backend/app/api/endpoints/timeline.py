from typing import List, Any, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowInstance
from app.application.audit_service import AuditService
from app.application.data_lineage_service import DataLineageService
from app.schemas.workflow import WorkflowTimelineResponse, TimelineEntry

router = APIRouter()
audit_service = AuditService()
lineage_service = DataLineageService()

@router.get("/{request_id}")
def get_unified_timeline(request_id: str, db: Session = Depends(get_db)):
    """Retrieve a unified timeline combining workflow steps, audit logs, and data lineage."""
    sr = db.query(ServiceRequest).filter_by(request_id=request_id).first()
    if sr is None:
        raise HTTPException(status_code=404, detail="Service request not found")

    correlation_id = sr.correlation_id

    # Get workflow timeline
    workflow = db.query(WorkflowInstance).filter_by(service_request_id=request_id).first()
    workflow_steps = []
    if workflow:
        for step in workflow.steps:
            duration_ms = None
            if step.started_at and step.completed_at:
                duration_ms = int((step.completed_at - step.started_at).total_seconds() * 1000)
            
            workflow_steps.append({
                "type": "workflow_step",
                "timestamp": step.started_at or step.created_at,
                "data": {
                    "step_name": step.step_name,
                    "status": step.status,
                    "attempt_count": step.attempt_count,
                    "duration_ms": duration_ms,
                    "error_message": step.error_message
                }
            })

    # Get audit logs
    audit_logs = audit_service.get_logs_by_correlation(db, correlation_id)
    audit_entries = []
    for log in audit_logs:
        audit_entries.append({
            "type": "audit_event",
            "timestamp": log.created_at,
            "data": {
                "event_type": log.event_type,
                "actor": log.actor,
                "target": log.target,
                "detail": log.detail,
                "outcome": log.outcome
            }
        })

    # Get data lineage
    lineage_records = lineage_service.get_lineage_by_correlation(db, correlation_id)
    lineage_entries = []
    for record in lineage_records:
        lineage_entries.append({
            "type": "data_lineage",
            "timestamp": record.created_at,
            "data": {
                "source_system": record.source_system,
                "source_field": record.source_field,
                "destination_system": record.destination_system,
                "destination_field": record.destination_field,
                "transformation": record.transformation
            }
        })

    # Combine and sort
    unified_timeline = workflow_steps + audit_entries + lineage_entries
    
    # Sort chronologically, handling potential None timestamps
    unified_timeline.sort(key=lambda x: x["timestamp"].timestamp() if x["timestamp"] else 0)

    return {
        "request_id": request_id,
        "correlation_id": correlation_id,
        "service_type": sr.service_type,
        "status": sr.status,
        "timeline": unified_timeline
    }
