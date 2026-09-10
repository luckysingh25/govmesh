import httpx
import logging
import json

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class IdentityConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.identity_url)

    async def fetch_data(self, citizen_id: str, correlation_id: str | None = None) -> ConnectorResult:
        try:
            headers = {"Authorization": "Bearer synthetic-department-token"}
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id
            response = await self.client.get(f"{self.base_url}/api/identity/{citizen_id}", headers=headers)
            response.raise_for_status()
            data = response.json()
            normalized = {
                "full_name": data["full_name"],
                "date_of_birth": data["date_of_birth"],
                "address": data["address"],
                "verification_status": data["verification_status"],
            }
            return ConnectorResult("identity", "success", normalized, protocol="REST", raw_response=self.bounded_payload(json.dumps(data, indent=2)), source_mapping={"full_name":"full_name","date_of_birth":"date_of_birth","address":"address","verification_status":"verification_status"})
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("identity_http_error status=%s", status)
            if status == 404:
                return ConnectorResult("identity", "not_found", {}, "Identity record was not found")
            return ConnectorResult("identity", "failed", {}, "Identity service returned an error")
        except httpx.TimeoutException:
            logger.warning("identity_timeout")
            return ConnectorResult("identity", "timeout", {}, "Identity service timed out")
        except httpx.RequestError:
            logger.warning("identity_unavailable")
            return ConnectorResult("identity", "unavailable", {}, "Identity service could not be reached")
        except (KeyError, TypeError, ValueError):
            logger.warning("identity_invalid_response")
            return ConnectorResult("identity", "invalid_response", {}, "Identity service returned an invalid response")
