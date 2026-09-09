from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.application.data_lineage_service import DataLineageService
from app.schemas.data_lineage import DataLineageResponse

router = APIRouter()
lineage_service = DataLineageService()

@router.get("/{correlation_id}", response_model=List[DataLineageResponse])
def get_lineage_by_correlation(correlation_id: str, db: Session = Depends(get_db)):
    """Retrieve all data lineage mapping records for a specific correlation ID."""
    records = lineage_service.get_lineage_by_correlation(db, correlation_id)
    return records
