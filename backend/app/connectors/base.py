import httpx
import logging
from dataclasses import dataclass
from typing import Any, Dict
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


@dataclass
class ConnectorResult:
    """Normalized result returned by every department adaptor."""
    department: str
    status: str
    data: Dict[str, Any]
    error: str | None = None
    protocol: str | None = None
    raw_response: str | None = None
    source_mapping: Dict[str, str] | None = None
    schema_version: int | None = None
    mapping_version: int | None = None
    external_job_id: str | None = None
    duration_ms: int | None = None

class BaseConnector(ABC):
    """Abstract base class for all department service connectors."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=5.0)

    @abstractmethod
    async def fetch_data(self, citizen_id: str, correlation_id: str | None = None) -> ConnectorResult:
        """
        Fetch data for a given citizen_id.
        All protocol-specific responses are adapted to a ConnectorResult.
        """
        pass
    
    async def close(self):
        await self.client.aclose()

    @staticmethod
    def bounded_payload(payload: str, limit: int = 16_384) -> str:
        return payload[:limit] + ("\n…truncated" if len(payload) > limit else "")
