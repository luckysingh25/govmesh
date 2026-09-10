from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.application.data_lineage_service import DataLineageService
from app.schemas.data_lineage import DataLineageResponse
from app.core.auth import get_current_user, ensure_citizen_access
from app.models.user import User
from app.models.service_request import ServiceRequest

router = APIRouter()
lineage_service = DataLineageService()

@router.get("/{correlation_id}", response_model=List[DataLineageResponse])
def get_lineage_by_correlation(correlation_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve all data lineage mapping records for a specific correlation ID."""
    request = db.query(ServiceRequest).filter_by(correlation_id=correlation_id).first()
    if request:
        ensure_citizen_access(current_user, request.citizen_id)
    records = lineage_service.get_lineage_by_correlation(db, correlation_id)
    return records
