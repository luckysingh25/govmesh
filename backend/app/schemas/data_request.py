from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class DataRequestResponse(BaseModel):
    id: int
    system_name: str
    status: str
    latency_ms: Optional[int]
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)
