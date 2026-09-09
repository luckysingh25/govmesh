"""Pydantic schemas for the Workflow API."""

from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class WorkflowStartRequest(BaseModel):
    """Body for POST /api/v1/workflows/start."""
    service_request_id: str


class WorkflowStepStatus(BaseModel):
    """Status of a single workflow step."""
    step_name: str
    step_index: int
    status: str
    attempt_count: int
    max_retries: int
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    protocol: Optional[str] = None
    raw_response: Optional[str] = None
    source_mapping: Optional[Dict[str, str]] = None
    normalized_output: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    schema_version: Optional[int] = None
    mapping_version: Optional[int] = None
    external_job_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowStatusResponse(BaseModel):
    """Response for GET /api/v1/workflows/{workflow_id}."""
    workflow_id: str
    service_request_id: str
    citizen_id: str
    definition_name: str
    status: str
    current_step_index: int
    steps: List[WorkflowStepStatus]
    insights: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TimelineEntry(BaseModel):
    """A single entry in the workflow timeline."""
    step_name: str
    step_index: int
    status: str
    attempt_count: int
    max_retries: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None


class WorkflowTimelineResponse(BaseModel):
    """Response for GET /api/v1/workflows/{workflow_id}/timeline."""
    workflow_id: str
    service_request_id: str
    overall_status: str
    created_at: datetime
    timeline: List[TimelineEntry]
