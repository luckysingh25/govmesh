from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import require_roles
from app.core.config import settings

from app.application.intelligence_service import IntelligenceService
from app.models.intelligence import SystemSchema, MappingSuggestion, ImpactAnalysis
from app.schemas.intelligence import (
    SchemaUploadRequest,
    SystemSchemaResponse,
    MappingSuggestionResponse,
    ImpactAnalysisResponse
)

router = APIRouter()
intel_service = IntelligenceService()

@router.post("/schemas/ingest", response_model=SystemSchemaResponse)
def ingest_schema(
    payload: SchemaUploadRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(require_roles(["admin", "data_steward"])),
):
    """Upload a new schema, parse fields, version it, and generate mappings/impact."""
    return intel_service.ingest_schema(db, payload.system_name, payload.schema_content)

@router.get("/schemas", response_model=List[SystemSchemaResponse])
def get_schemas(db: Session = Depends(get_db)):
    """List all schemas and their fields."""
    return db.query(SystemSchema).order_by(SystemSchema.created_at.desc()).all()

@router.get("/suggestions", response_model=List[MappingSuggestionResponse])
def get_suggestions(status: str = "pending", db: Session = Depends(get_db)):
    """List semantic mapping suggestions."""
    return db.query(MappingSuggestion).filter_by(status=status).order_by(MappingSuggestion.confidence_score.desc()).all()

@router.post("/suggestions/{suggestion_id}/approve", response_model=MappingSuggestionResponse)
def approve_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_roles(["admin", "data_steward"])),
):
    """Human approval of a suggested mapping."""
    sug = intel_service.approve_suggestion(db, suggestion_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return sug

@router.post("/suggestions/{suggestion_id}/reject", response_model=MappingSuggestionResponse)
def reject_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    _current_user=Depends(require_roles(["admin", "data_steward"])),
):
    """Human rejection of a suggested mapping."""
    sug = intel_service.reject_suggestion(db, suggestion_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return sug

@router.get("/impact", response_model=List[ImpactAnalysisResponse])
def get_all_impact_analyses(db: Session = Depends(get_db)):
    """Retrieve all impact analysis reports."""
    return db.query(ImpactAnalysis).order_by(ImpactAnalysis.created_at.desc()).all()

@router.post("/demo/trigger")
def trigger_demo_scenario(db: Session = Depends(get_db)):
    """Seed the demo scenario where owner_name changes to property_owner_name."""
    if settings.environment.casefold() not in {"development", "demo", "test"}:
        raise HTTPException(status_code=404, detail="Not found")
    # V1 Schema
    v1_schema = {
        "properties": {
            "propertyId": {"type": "string"},
            "ownerName": {"type": "string"},
            "propertyAddress": {"type": "string"},
            "propertyType": {"type": "string"}
        },
        "required": ["propertyId", "ownerName"]
    }
    
    # V2 Schema (Breaking change)
    v2_schema = {
        "properties": {
            "propertyId": {"type": "string"},
            "propertyOwnerName": {"type": "string"}, # RENAMED
            "propertyAddress": {"type": "string"},
            "propertyType": {"type": "string"}
        },
        "required": ["propertyId", "propertyOwnerName"]
    }
    
    existing = (
        db.query(SystemSchema)
        .filter_by(system_name="Property System")
        .order_by(SystemSchema.version.asc())
        .all()
    )
    if not existing:
        intel_service.ingest_schema(db, "Property System", v1_schema)
        intel_service.ingest_schema(db, "Property System", v2_schema)
    elif max(schema.version for schema in existing) == 1:
        intel_service.ingest_schema(db, "Property System", v2_schema)

    return {"message": "Demo scenario is ready.", "versions": 2}
