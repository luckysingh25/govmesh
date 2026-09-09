from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class DataLineage(Base):
    """Tracks field-level data flow from source systems to the final response."""
    __tablename__ = "data_lineage"

    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String, index=True, nullable=False)
    service_request_id = Column(String, index=True, nullable=True)
    
    source_system = Column(String, nullable=False) # e.g. "Identity Connector", "Tax System"
    source_field = Column(String, nullable=False) # e.g. "full_name", "tax_status"
    
    destination_system = Column(String, nullable=False) # e.g. "GovMesh Unified Response"
    destination_field = Column(String, nullable=False) # e.g. "citizen.name"
    
    transformation = Column(String, nullable=True) # e.g. "exact match", "normalized format"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
