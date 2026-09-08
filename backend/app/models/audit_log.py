from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class AuditLog(Base):
    """Immutable audit trail for security and policy events."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, index=True, nullable=True)
    event_type = Column(String, index=True, nullable=False) # e.g. "Policy Decision", "Consent Granted"
    actor = Column(String, nullable=False) # "System Engine", "Citizen (CIT-1001)"
    target = Column(String, nullable=False) # "CIT-1001", "GovMesh Core"
    detail = Column(String, nullable=False)
    outcome = Column(String, nullable=False) # "allow", "success", "deny", "error"
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
