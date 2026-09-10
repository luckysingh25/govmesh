import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.consent import CitizenConsent
from app.application.audit_service import AuditService

logger = logging.getLogger(__name__)


class ConsentService:
    """Manage citizen consent records."""

    def __init__(self):
        self._audit = AuditService()

    def grant(
        self,
        db: Session,
        citizen_id: str,
        service_type: str,
        departments: list[str],
        ttl_hours: int = 24,
    ) -> CitizenConsent:
        now = datetime.now(timezone.utc)
        active = (
            db.query(CitizenConsent)
            .filter(
                CitizenConsent.citizen_id == citizen_id,
                CitizenConsent.service_type == service_type,
                CitizenConsent.revoked_at.is_(None),
                CitizenConsent.expires_at > now,
            )
            .order_by(CitizenConsent.granted_at.desc())
            .first()
        )
        if active is not None:
            active.revoked_at = now
        consent = CitizenConsent(
            citizen_id=citizen_id,
            service_type=service_type,
            departments=list(departments),
            granted_at=now,
            expires_at=now + timedelta(hours=ttl_hours),
        )
        db.add(consent)
        db.commit()
        db.refresh(consent)
        
        self._audit.log_event(
            db,
            event_type="Consent Granted",
            actor=f"Citizen ({citizen_id})",
            target="GovMesh Core",
            detail=f"Granted access to: {', '.join(departments)}",
            outcome="success"
        )
        
        logger.info("consent_granted citizen_id=%s service_type=%s id=%s", citizen_id, service_type, consent.id)
        return consent

    def revoke(self, db: Session, consent_id: int) -> Optional[CitizenConsent]:
        consent = db.query(CitizenConsent).filter(CitizenConsent.id == consent_id).first()
        if consent is None:
            return None
        consent.revoked_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(consent)
        
        self._audit.log_event(
            db,
            event_type="Consent Revoked",
            actor=f"Citizen ({consent.citizen_id})",
            target="GovMesh Core",
            detail="Revoked access manually",
            outcome="success"
        )
        
        logger.info("consent_revoked id=%s", consent_id)
        return consent

    def get_active(
        self, db: Session, citizen_id: str, service_type: str
    ) -> Optional[CitizenConsent]:
        """Return the most recent active (not revoked, not expired) consent."""
        now = datetime.now(timezone.utc)
        return (
            db.query(CitizenConsent)
            .filter(
                CitizenConsent.citizen_id == citizen_id,
                CitizenConsent.service_type == service_type,
                CitizenConsent.revoked_at.is_(None),
                CitizenConsent.expires_at > now,
            )
            .order_by(CitizenConsent.granted_at.desc())
            .first()
        )
