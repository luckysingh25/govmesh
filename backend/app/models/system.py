from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.sql import func
from app.db.session import Base

class System(Base):
    """Tracks integrated backend department systems."""
    __tablename__ = "systems"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    system_type = Column(String, nullable=False) # Core Registry, State Dept, etc.
    protocol = Column(String, nullable=False) # REST, SOAP, gRPC, etc.
    status = Column(String, nullable=False, default="Online") # Online, Degraded, Offline
    uptime_percent = Column(Float, nullable=False, default=100.0)
    latency_ms = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
