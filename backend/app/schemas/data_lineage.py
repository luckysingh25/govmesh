from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List

class DataLineageResponse(BaseModel):
    id: int
    correlation_id: str
    service_request_id: Optional[str] = None
    source_system: str
    source_field: str
    destination_system: str
    destination_field: str
    transformation: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
