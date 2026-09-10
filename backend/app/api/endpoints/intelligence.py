from typing import List, Dict, Any
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.auth import require_roles
from app.application.audit_service import AuditService
from app.models.user import User
from app.core.config import settings

from app.application.intelligence_service import IntelligenceService
from app.models.intelligence import SystemSchema, SchemaField, MappingSuggestion, ImpactAnalysis
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
    current_user: User = Depends(require_roles(["admin", "data_steward"])),
):
    """Upload a new schema, parse fields, version it, and generate mappings/impact."""
    return intel_service.ingest_schema(db, payload.system_name, payload.schema_content)

@router.get("/schemas", response_model=List[SystemSchemaResponse])
def get_schemas(db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward", "civic_employee"]))):
    """List all schemas and their fields."""
    return db.query(SystemSchema).order_by(SystemSchema.created_at.desc()).all()

@router.get("/suggestions", response_model=List[MappingSuggestionResponse])
def get_suggestions(status: str = "pending", db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward"]))):
    """List semantic mapping suggestions."""
    return db.query(MappingSuggestion).filter_by(status=status).order_by(MappingSuggestion.confidence_score.desc()).all()

@router.post("/suggestions/{suggestion_id}/approve", response_model=MappingSuggestionResponse)
def approve_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "data_steward"])),
):
    """Human approval of a suggested mapping."""
    try:
        sug = intel_service.approve_suggestion(db, suggestion_id, actor=current_user.email)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    AuditService().log_event(db=db, event_type="Mapping Approved", actor=current_user.email, target=f"mapping:{sug.id}", detail=f"mapping_version={sug.mapping_version}; target={sug.target_field}", outcome="approved")
    return sug

@router.post("/suggestions/{suggestion_id}/reject", response_model=MappingSuggestionResponse)
def reject_suggestion(
    suggestion_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["admin", "data_steward"])),
):
    """Human rejection of a suggested mapping."""
    sug = intel_service.reject_suggestion(db, suggestion_id, actor=current_user.email)
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    AuditService().log_event(db=db, event_type="Mapping Rejected", actor=current_user.email, target=f"mapping:{sug.id}", detail=f"target={sug.target_field}", outcome="rejected")
    return sug

@router.get("/impact", response_model=List[ImpactAnalysisResponse])
def get_all_impact_analyses(db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward", "civic_employee"]))):
    """Retrieve all impact analysis reports."""
    return db.query(ImpactAnalysis).order_by(ImpactAnalysis.created_at.desc()).all()

def _require_demo_controls() -> None:
    if settings.environment.casefold() not in {"development", "demo", "test"} or not settings.demo_controls_enabled or not settings.demo_control_key:
        raise HTTPException(status_code=404, detail="Not found")


@router.post("/demo/trigger")
def trigger_demo_scenario(db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward"]))):
    """Seed the demo scenario where owner_name changes to property_owner_name."""
    _require_demo_controls()
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


async def _property_control(path: str) -> dict:
    _require_demo_controls()
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.put(
            f"{settings.property_url.rstrip('/')}{path}",
            headers={"X-Demo-Control-Key": settings.demo_control_key},
        )
    if not response.is_success:
        raise HTTPException(status_code=502, detail="Synthetic Property control rejected the request")
    return response.json()


@router.put("/demo/property/schema/{version}")
async def set_property_schema(version: int, _current_user: User = Depends(require_roles(["admin", "data_steward"]))):
    if version not in {1, 2}:
        raise HTTPException(status_code=422, detail="Supported schema versions are 1 and 2")
    return await _property_control(f"/demo/schema/{version}")


@router.put("/demo/property/availability/{available}")
async def set_property_availability(available: bool, _current_user: User = Depends(require_roles(["admin", "data_steward"]))):
    return await _property_control(f"/demo/availability/{str(available).lower()}")


@router.post("/demo/reset")
async def reset_demo(db: Session = Depends(get_db), _current_user: User = Depends(require_roles(["admin", "data_steward"]))):
    _require_demo_controls()
    async with httpx.AsyncClient(timeout=3.0) as client:
        response = await client.post(
            f"{settings.property_url.rstrip('/')}/demo/reset",
            headers={"X-Demo-Control-Key": settings.demo_control_key},
        )
    if not response.is_success:
        raise HTTPException(status_code=502, detail="Synthetic Property reset failed")
    schemas = db.query(SystemSchema).filter_by(system_name="Property System").all()
    schema_ids = [schema.id for schema in schemas]
    if schema_ids:
        fields = db.query(SchemaField).filter(SchemaField.schema_id.in_(schema_ids)).all()
        field_ids = [field.id for field in fields]
        if field_ids:
            for suggestion in db.query(MappingSuggestion).filter(MappingSuggestion.source_field_id.in_(field_ids)).all():
                db.delete(suggestion)
        for field in fields:
            db.delete(field)
    for impact in db.query(ImpactAnalysis).filter_by(system_name="Property System").all():
        db.delete(impact)
    for schema in schemas:
        db.delete(schema)
    db.commit()
    return {"message":"Synthetic Property demo state reset", "property":response.json()}
