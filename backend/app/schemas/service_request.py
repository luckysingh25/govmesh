from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any
from datetime import datetime

class ServiceRequestCreate(BaseModel):
    citizen_id: str = Field(..., description="The ID of the citizen", examples=["CIT-1001"])
    service_type: str = Field(..., description="Type of service requested", examples=["business_registration"])

class DepartmentResponse(BaseModel):
    status: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CitizenInfo(BaseModel):
    citizen_id: str
    name: Optional[str] = None
    address: Optional[str] = None

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

    model_config = ConfigDict(from_attributes=True)

class ServiceRequestListResponse(BaseModel):
    id: int
    request_id: str
    citizen_id: str
    service_type: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
