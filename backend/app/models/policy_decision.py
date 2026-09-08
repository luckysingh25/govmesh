from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base


class PolicyDecision(Base):
    """Audit trail of every policy evaluation for a service request."""
    __tablename__ = "policy_decisions"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(String, index=True, nullable=False)
    service_type = Column(String, nullable=False)
    correlation_id = Column(String, index=True, nullable=False)
    decision = Column(String, nullable=False)   # "allow" or "deny"
    reason = Column(String, nullable=True)       # human-readable explanation
    decided_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
