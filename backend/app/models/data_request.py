from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.session import Base

class DataRequest(Base):
    """Tracks the lifecycle of an individual connector sub-request."""
    __tablename__ = "data_requests"

    id = Column(Integer, primary_key=True, index=True)
    service_request_id = Column(String, index=True, nullable=False) # References ServiceRequest.request_id
    system_name = Column(String, nullable=False) # e.g. 'identity', 'tax'
    status = Column(String, nullable=False, default="pending") # pending, success, failed, denied
    latency_ms = Column(Integer, nullable=True)
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
