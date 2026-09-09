from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime

class SchemaUploadRequest(BaseModel):
    system_name: str
    schema_content: Dict[str, Any]

class SchemaFieldResponse(BaseModel):
    id: int
    field_name: str
    normalized_name: str
    field_type: str
    is_required: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class SystemSchemaResponse(BaseModel):
    id: int
    system_name: str
    version: int
    status: str
    created_at: datetime
    fields: List[SchemaFieldResponse] = []
    model_config = ConfigDict(from_attributes=True)

class MappingSuggestionResponse(BaseModel):
    id: int
    source_field_id: int
    target_field: str
    confidence_score: float
    mapping_type: str
    status: str
    created_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    mapping_version: Optional[int] = None
    source_field: Optional[SchemaFieldResponse] = None
    model_config = ConfigDict(from_attributes=True)

class ImpactAnalysisResponse(BaseModel):
    id: int
    system_name: str
    old_version: Optional[int]
    new_version: int
    analysis_result: Dict[str, Any]
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
