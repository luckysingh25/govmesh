from pydantic import BaseModel, ConfigDict
from datetime import datetime

class SystemBase(BaseModel):
    name: str
    system_type: str
    protocol: str
    status: str = "Online"
    uptime_percent: float = 100.0
    latency_ms: int = 0

class SystemCreate(SystemBase):
    pass

class SystemResponse(SystemBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
