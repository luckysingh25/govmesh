from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime
import re

from app.core.service_types import KNOWN_DEPARTMENTS, ServiceType


class ConsentGrantRequest(BaseModel):
    citizen_id: str = Field(..., examples=["CIT-1001"])
    service_type: ServiceType = Field(..., examples=["business_registration"])
    departments: list[str] = Field(
        ...,
        description="Department names the citizen consents to",
        examples=[["identity", "property", "municipality", "tax"]],
    )
    ttl_hours: int = Field(24, ge=1, le=720, description="Hours until consent expires")

    @field_validator("citizen_id")
    @classmethod
    def validate_citizen_id(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not re.fullmatch(r"CIT-\d{4}", normalized):
            raise ValueError("citizen_id must use the format CIT-1001")
        return normalized

    @field_validator("departments")
    @classmethod
    def validate_departments(cls, value: list[str]) -> list[str]:
        normalized = [department.strip().lower() for department in value]
        unknown = sorted(set(normalized) - set(KNOWN_DEPARTMENTS))
        if unknown:
            raise ValueError(f"unknown departments: {', '.join(unknown)}")
        if len(normalized) != len(set(normalized)):
            raise ValueError("departments must not contain duplicates")
        if not normalized:
            raise ValueError("at least one department is required")
        return normalized


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
