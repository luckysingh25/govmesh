import logging
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog

logger = logging.getLogger(__name__)

class AuditService:
    """Records security, policy, and system access events."""
    
    def log_event(
        self,
        db: Session,
        event_type: str,
        actor: str,
        target: str,
        detail: str,
        outcome: str,
        correlation_id: str | None = None,
        commit: bool = True,
    ) -> AuditLog:
        record = AuditLog(
            correlation_id=correlation_id,
            event_type=event_type,
            actor=actor,
            target=target,
            detail=detail,
            outcome=outcome,
        )
        db.add(record)
        if commit:
            db.commit()
        logger.info(f"audit_event: {event_type} | {actor} -> {target} | {outcome} | {detail}")
        return record

    def get_logs_by_correlation(self, db: Session, correlation_id: str) -> list[AuditLog]:
        return (
            db.query(AuditLog)
            .filter(AuditLog.correlation_id == correlation_id)
            .order_by(AuditLog.created_at.desc())
            .all()
        )

    def get_recent_logs(self, db: Session, limit: int = 50) -> list[AuditLog]:
        return (
            db.query(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
            .all()
        )
