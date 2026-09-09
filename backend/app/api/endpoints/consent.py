from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.consent_service import ConsentService
from app.db.session import get_db
from app.schemas.consent import ConsentGrantRequest, ConsentResponse, ConsentRevokeResponse
from app.core.service_types import ServiceType
from app.core.auth import get_current_user, ensure_citizen_access
from app.models.user import User
from app.models.consent import CitizenConsent

router = APIRouter()
_service = ConsentService()


@router.post("", response_model=ConsentResponse, status_code=201)
@router.post("/", response_model=ConsentResponse, status_code=201, include_in_schema=False)
def grant_consent(payload: ConsentGrantRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_citizen_access(current_user, payload.citizen_id)
    consent = _service.grant(
        db,
        citizen_id=payload.citizen_id,
        service_type=payload.service_type.value,
        departments=payload.departments,
        ttl_hours=payload.ttl_hours,
    )
    return consent


@router.delete("/{consent_id}", response_model=ConsentRevokeResponse)
def revoke_consent(consent_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.get(CitizenConsent, consent_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="Consent record not found")
    ensure_citizen_access(current_user, existing.citizen_id)
    consent = _service.revoke(db, consent_id)
    if consent is None:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return ConsentRevokeResponse(id=consent.id, revoked_at=consent.revoked_at)


@router.get("/{citizen_id}/{service_type}", response_model=ConsentResponse)
def get_active_consent(citizen_id: str, service_type: ServiceType, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_citizen_access(current_user, citizen_id.strip().upper())
    consent = _service.get_active(db, citizen_id.strip().upper(), service_type.value)
    if consent is None:
        raise HTTPException(status_code=404, detail="No active consent found")
    return consent
