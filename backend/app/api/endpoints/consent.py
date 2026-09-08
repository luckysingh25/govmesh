from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.application.consent_service import ConsentService
from app.db.session import get_db
from app.schemas.consent import ConsentGrantRequest, ConsentResponse, ConsentRevokeResponse

router = APIRouter()
_service = ConsentService()


@router.post("", response_model=ConsentResponse, status_code=201)
@router.post("/", response_model=ConsentResponse, status_code=201, include_in_schema=False)
def grant_consent(payload: ConsentGrantRequest, db: Session = Depends(get_db)):
    consent = _service.grant(
        db,
        citizen_id=payload.citizen_id,
        service_type=payload.service_type,
        departments=payload.departments,
        ttl_hours=payload.ttl_hours,
    )
    return consent


@router.delete("/{consent_id}", response_model=ConsentRevokeResponse)
def revoke_consent(consent_id: int, db: Session = Depends(get_db)):
    consent = _service.revoke(db, consent_id)
    if consent is None:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return ConsentRevokeResponse(id=consent.id, revoked_at=consent.revoked_at)


@router.get("/{citizen_id}/{service_type}", response_model=ConsentResponse)
def get_active_consent(citizen_id: str, service_type: str, db: Session = Depends(get_db)):
    consent = _service.get_active(db, citizen_id, service_type)
    if consent is None:
        raise HTTPException(status_code=404, detail="No active consent found")
    return consent
