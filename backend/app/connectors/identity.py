import logging
from app.connectors.base import BaseConnector, ConnectorResult
import httpx

logger = logging.getLogger(__name__)

from app.core.config import settings

class IdentityConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.identity_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            # Simulate a JWT token requirement (just an Authorization header)
            headers = {"Authorization": "Bearer sim_token_123"}
            response = await self.client.get(f"{self.base_url}/api/identity/{citizen_id}", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            return ConnectorResult("identity", "success", {
                "full_name": data["full_name"],
                "date_of_birth": data["date_of_birth"],
                "address": data["address"],
            })
        except httpx.HTTPStatusError as e:
            logger.error(f"Identity API HTTP error: {e}")
            return ConnectorResult("identity", "failed", {}, f"HTTP Error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Identity API Request error: {e}")
            return ConnectorResult("identity", "failed", {}, "Identity service unavailable")
        except Exception as e:
            logger.exception("Unexpected error in IdentityConnector")
            return ConnectorResult("identity", "failed", {}, str(e))
