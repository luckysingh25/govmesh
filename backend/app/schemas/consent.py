from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ConsentGrantRequest(BaseModel):
    citizen_id: str = Field(..., examples=["CIT-1001"])
    service_type: str = Field(..., examples=["business_registration"])
    departments: list[str] = Field(
        ...,
        description="Department names the citizen consents to",
        examples=[["identity", "property", "municipality", "tax"]],
    )
    ttl_hours: int = Field(24, description="Hours until consent expires")


class ConsentResponse(BaseModel):
    id: int
    citizen_id: str
    service_type: str
    departments: list[str]
    granted_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ConsentRevokeResponse(BaseModel):
    id: int
    revoked_at: datetime
    message: str = "Consent revoked successfully"
