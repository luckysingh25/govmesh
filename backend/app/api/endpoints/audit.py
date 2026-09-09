from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.application.audit_service import AuditService
from app.schemas.audit import AuditLogResponse
from app.core.auth import require_roles, get_current_user, ensure_citizen_access
from app.models.user import User
from app.models.service_request import ServiceRequest

router = APIRouter()
audit_service = AuditService()

@router.get("", response_model=List[AuditLogResponse])
def get_global_audit_logs(limit: int = 50, db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward", "civic_employee"]))):
    """Retrieve the most recent audit logs globally."""
    return audit_service.get_recent_logs(db, limit)

@router.get("/correlation/{correlation_id}", response_model=List[AuditLogResponse])
def get_audit_logs_by_correlation(correlation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve all audit logs related to a specific correlation ID."""
    request = db.query(ServiceRequest).filter_by(correlation_id=correlation_id).first()
    if request:
        ensure_citizen_access(current_user, request.citizen_id)
    elif current_user.role not in {"admin", "data_steward", "civic_employee"}:
        raise HTTPException(status_code=404, detail="No audit logs found for this correlation ID")
    logs = audit_service.get_logs_by_correlation(db, correlation_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found for this correlation ID")
    return logs
