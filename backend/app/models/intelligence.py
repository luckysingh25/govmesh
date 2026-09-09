from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class SystemSchema(Base):
    """Stores versions of ingested schemas for a system."""
    __tablename__ = "system_schemas"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, index=True, nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(JSON, nullable=False)
    status = Column(String, default="active") # active, superseded
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    fields = relationship("SchemaField", back_populates="schema")


class SchemaField(Base):
    """Normalized fields extracted from a SystemSchema."""
    __tablename__ = "schema_fields"

    id = Column(Integer, primary_key=True, index=True)
    schema_id = Column(Integer, ForeignKey("system_schemas.id"), nullable=False)
    field_name = Column(String, nullable=False) # Original name (e.g., ownerName)
    normalized_name = Column(String, nullable=False) # Normalized (e.g., owner_name)
    field_type = Column(String, nullable=False)
    is_required = Column(String, nullable=True) # "true" or "false" string, or boolean if preferred. Using string for schema flexibility.
    
    schema = relationship("SystemSchema", back_populates="fields")
    mappings = relationship("MappingSuggestion", back_populates="source_field")


class MappingSuggestion(Base):
    """AI/Rule-based semantic mapping suggestions to GovMesh canonical fields."""
    __tablename__ = "mapping_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    source_field_id = Column(Integer, ForeignKey("schema_fields.id"), nullable=False)
    target_field = Column(String, nullable=False) # e.g. "citizen.name"
    confidence_score = Column(Float, nullable=False) # 0.0 to 1.0
    mapping_type = Column(String, nullable=False) # exact, normalized, semantic, transformation-required, incompatible
    status = Column(String, default="pending") # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    source_field = relationship("SchemaField", back_populates="mappings")


class ImpactAnalysis(Base):
    """Stores the analysis results when a schema changes."""
    __tablename__ = "impact_analyses"

    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String, index=True, nullable=False)
    old_version = Column(Integer, nullable=True)
    new_version = Column(Integer, nullable=False)
    analysis_result = Column(JSON, nullable=False) # Contains details on broken workflows, orphaned mappings, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
