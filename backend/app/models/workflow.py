"""Workflow models for the orchestration engine.

WorkflowDefinition — reusable template listing ordered department steps.
WorkflowInstance   — one execution of a workflow, tied to a ServiceRequest.
WorkflowStepInstance — tracks each department step within a workflow run.
"""

import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


def _generate_uuid() -> str:
    return uuid.uuid4().hex[:12].upper()


class WorkflowDefinition(Base):
    """Reusable workflow template (seeded once per service type)."""
    __tablename__ = "workflow_definitions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)  # e.g. "business_registration"
    description = Column(String, nullable=True)
    steps = Column(JSON, nullable=False)  # ordered list: ["identity","property","municipality","tax"]
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    instances = relationship("WorkflowInstance", back_populates="definition")


class WorkflowInstance(Base):
    """One execution of a workflow, tied to a ServiceRequest."""
    __tablename__ = "workflow_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, nullable=False, index=True, default=_generate_uuid)
    definition_id = Column(Integer, ForeignKey("workflow_definitions.id"), nullable=False)
    service_request_id = Column(String, nullable=False, index=True)   # → ServiceRequest.request_id
    citizen_id = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="pending")        # pending, running, success, failed, partially_completed
    current_step_index = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    definition = relationship("WorkflowDefinition", back_populates="instances")
    steps = relationship(
        "WorkflowStepInstance",
        back_populates="workflow_instance",
        order_by="WorkflowStepInstance.step_index",
    )


class WorkflowStepInstance(Base):
    """Tracks an individual department step within a workflow run."""
    __tablename__ = "workflow_step_instances"

    id = Column(Integer, primary_key=True, index=True)
    workflow_instance_id = Column(Integer, ForeignKey("workflow_instances.id"), nullable=False, index=True)
    step_name = Column(String, nullable=False)                 # "identity", "property", etc.
    step_index = Column(Integer, nullable=False)               # 0-based position in pipeline
    status = Column(String, nullable=False, default="pending") # pending, running, success, failed, retrying
    attempt_count = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=3)
    result_data = Column(JSON, nullable=True)                  # connector result payload
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    next_retry_at = Column(DateTime(timezone=True), nullable=True)
    protocol = Column(String, nullable=True)
    raw_response = Column(Text, nullable=True)
    source_mapping = Column(JSON, nullable=True)
    normalized_output = Column(JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    correlation_id = Column(String, nullable=True)
    schema_version = Column(Integer, nullable=True)
    mapping_version = Column(Integer, nullable=True)
    external_job_id = Column(String, nullable=True)

    workflow_instance = relationship("WorkflowInstance", back_populates="steps")
