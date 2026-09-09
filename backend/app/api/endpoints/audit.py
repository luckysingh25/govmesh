from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.application.audit_service import AuditService
from app.schemas.audit import AuditLogResponse

router = APIRouter()
audit_service = AuditService()

@router.get("", response_model=List[AuditLogResponse])
def get_global_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve the most recent audit logs globally."""
    return audit_service.get_recent_logs(db, limit)

@router.get("/correlation/{correlation_id}", response_model=List[AuditLogResponse])
def get_audit_logs_by_correlation(correlation_id: str, db: Session = Depends(get_db)):
    """Retrieve all audit logs related to a specific correlation ID."""
    logs = audit_service.get_logs_by_correlation(db, correlation_id)
    if not logs:
        raise HTTPException(status_code=404, detail="No audit logs found for this correlation ID")
    return logs
