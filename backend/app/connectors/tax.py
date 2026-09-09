import httpx
import logging

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class TaxConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.tax_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            job = await self.client.post(f"{self.base_url}/api/tax/requests/{citizen_id}")
            job.raise_for_status()
            job_data = job.json()
            if job_data.get("status") == "pending":
                return ConnectorResult("tax", "pending", {"tax_status": "PENDING"})
            job_id = job_data["job_id"]
            response = await self.client.get(f"{self.base_url}/api/tax/requests/{job_id}")
            response.raise_for_status()
            result_payload = response.json()
            if result_payload.get("status") == "pending":
                return ConnectorResult("tax", "pending", {"tax_status": "PENDING"})
            data = result_payload["result"]
            return ConnectorResult("tax", "success", {
                "tax_id": data["taxId"],
                "taxpayer_name": data["taxpayerName"],
                "tax_status": data["taxStatus"],
                "outstanding_amount": data["outstandingAmount"],
                "assessment_year": data["assessmentYear"],
            })
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("tax_http_error status=%s", status)
            if status == 404:
                return ConnectorResult("tax", "not_found", {}, "Tax record was not found")
            return ConnectorResult("tax", "failed", {}, "Tax service returned an error")
        except httpx.TimeoutException:
            logger.warning("tax_timeout")
            return ConnectorResult("tax", "timeout", {}, "Tax service timed out")
        except httpx.RequestError:
            logger.warning("tax_unavailable")
            return ConnectorResult("tax", "unavailable", {}, "Tax service could not be reached")
        except (KeyError, TypeError, ValueError):
            logger.warning("tax_invalid_response")
            return ConnectorResult("tax", "invalid_response", {}, "Tax service returned an invalid response")
