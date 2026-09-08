from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AuditLogResponse(BaseModel):
    id: int
    correlation_id: Optional[str]
    event_type: str
    actor: str
    target: str
    detail: str
    outcome: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
