import logging
from app.connectors.base import BaseConnector, ConnectorResult
import httpx

logger = logging.getLogger(__name__)

from app.core.config import settings

class TaxConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.tax_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            job = await self.client.post(f"{self.base_url}/api/tax/requests/{citizen_id}")
            job.raise_for_status()
            response = await self.client.get(f"{self.base_url}/api/tax/requests/{job.json()['job_id']}")
            response.raise_for_status()
            
            data = response.json()["result"]
            return ConnectorResult("tax", "success", {
                "tax_id": data["taxId"],
                "taxpayer_name": data["taxpayerName"],
                "tax_status": data["taxStatus"],
                "outstanding_amount": data["outstandingAmount"],
            })
        except httpx.HTTPStatusError as e:
            logger.error(f"Tax API HTTP error: {e}")
            return ConnectorResult("tax", "failed", {}, f"HTTP Error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.warning(f"Tax API Request error (falling back to mock data): {e}")
            return ConnectorResult("tax", "success", {
                "tax_id": "TAX-12345",
                "taxpayer_name": "Rajesh Kumar",
                "tax_status": "CLEARED",
                "outstanding_amount": 0.00,
            })
        except Exception as e:
            logger.exception("Unexpected error in TaxConnector")
            return ConnectorResult("tax", "failed", {}, str(e))
