from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.db.session import Base


class CitizenConsent(Base):
    """Records a citizen's explicit consent for a service type and set of departments."""
    __tablename__ = "citizen_consents"

    id = Column(Integer, primary_key=True, index=True)
    citizen_id = Column(String, index=True, nullable=False)
    service_type = Column(String, nullable=False)
    # JSON list of department names the citizen consented to, e.g. ["identity","property"]
    departments = Column(JSON, nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
