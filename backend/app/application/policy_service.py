import logging
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.consent_service import ConsentService
from app.application.audit_service import AuditService
from app.core.service_types import required_departments
from app.models.policy_decision import PolicyDecision

logger = logging.getLogger(__name__)

@dataclass
class PolicyResult:
    """In-memory result before it is persisted."""
    decision: str     # "allow" or "deny"
    reason: str
    consent_id: int | None = None


class PolicyService:
    """Minimal policy engine: checks active consent before allowing department access."""

    def __init__(self) -> None:
        self._consent = ConsentService()
        self._audit = AuditService()

    def evaluate(
        self, db: Session, citizen_id: str, service_type: str, correlation_id: str
    ) -> PolicyResult:
        consent = self._consent.get_active(db, citizen_id, service_type)

        if consent is None:
            result = PolicyResult("deny", "No active consent for this citizen and service type")
        else:
            consented = set(consent.departments)
            required = set(required_departments(service_type))
            missing = required - consented
            if missing:
                result = PolicyResult(
                    "deny",
                    f"Consent does not cover departments: {', '.join(sorted(missing))}",
                    consent_id=consent.id,
                )
            else:
                result = PolicyResult("allow", "Active consent covers all departments", consent_id=consent.id)

        # Persist the decision for audit via dedicated table
        record = PolicyDecision(
            citizen_id=citizen_id,
            service_type=service_type,
            correlation_id=correlation_id,
            decision=result.decision,
            reason=result.reason,
        )
        db.add(record)
        
        # Write to unified audit log
        self._audit.log_event(
            db,
            event_type="Policy Decision",
            actor="System Engine",
            target=citizen_id,
            detail=result.reason,
            outcome=result.decision,
            correlation_id=correlation_id
        )
        
        db.commit()

        logger.info(
            "policy_evaluated citizen_id=%s decision=%s reason=%s correlation_id=%s",
            citizen_id, result.decision, result.reason, correlation_id,
        )
        return result
