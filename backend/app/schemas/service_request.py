from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, Dict, Any, Literal
from datetime import datetime
import re

from app.core.service_types import ServiceType

class ServiceRequestCreate(BaseModel):
    citizen_id: str = Field(..., description="The ID of the citizen", examples=["CIT-1001"])
    service_type: ServiceType = Field(..., description="Type of service requested", examples=["business_registration"])

    @field_validator("citizen_id")
    @classmethod
    def validate_citizen_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"CIT-\d{4}", normalized):
            raise ValueError("citizen_id must use the format CIT-1001")
        return normalized

class DepartmentResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CitizenInfo(BaseModel):
    citizen_id: str
    name: Optional[str] = None
    address: Optional[str] = None

class IntelligenceInsight(BaseModel):
    rule_id: str
    severity: Literal["info", "warning"]
    message: str

class ServiceRequestResponse(BaseModel):
    request_id: str
    correlation_id: str
    citizen: CitizenInfo
    identity: DepartmentResponse
    property: DepartmentResponse
    municipality: DepartmentResponse
    tax: DepartmentResponse
    overall_status: str
    consent_id: Optional[int] = None
    policy_decision: Optional[str] = None
    insights: list[IntelligenceInsight] = Field(default_factory=list)
    workflow_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ServiceRequestListResponse(BaseModel):
    id: int
    request_id: str
    citizen_id: str
    service_type: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    workflow_id: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)
