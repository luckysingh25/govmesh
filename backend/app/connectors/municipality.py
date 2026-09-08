import logging
from app.connectors.base import BaseConnector, ConnectorResult
import httpx

logger = logging.getLogger(__name__)

from app.core.config import settings

class MunicipalityConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.municipality_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            # Simulate API key authentication
            headers = {"x-api-key": "sim_municipality_key"}
            response = await self.client.get(f"{self.base_url}/api/municipality/{citizen_id}", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return ConnectorResult("municipality", "success", {
                "municipal_id": data["municipal_id"],
                "resident_name": data["resident_name"],
                "ward": data["ward"],
                "address": data["address"],
            })
        except httpx.HTTPStatusError as e:
            logger.error(f"Municipality API HTTP error: {e}")
            return ConnectorResult("municipality", "failed", {}, f"HTTP Error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Municipality API Request error: {e}")
            return ConnectorResult("municipality", "failed", {}, "Municipality service unavailable")
        except Exception as e:
            logger.exception("Unexpected error in MunicipalityConnector")
            return ConnectorResult("municipality", "failed", {}, str(e))
