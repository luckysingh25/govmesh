import httpx
import logging
import json

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class MunicipalityConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.municipality_url)

    async def fetch_data(self, citizen_id: str, correlation_id: str | None = None) -> ConnectorResult:
        try:
            headers = {"x-api-key": "sim_municipality_key"}
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id
            response = await self.client.get(f"{self.base_url}/api/municipality/{citizen_id}", headers=headers)
            response.raise_for_status()
            
            data = response.json()
            normalized = {
                "municipal_id": data["municipal_id"],
                "resident_name": data["resident_name"],
                "ward": data["ward"],
                "address": data["address"],
                "registration_status": data["registration_status"],
            }
            return ConnectorResult("municipality", "success", normalized, protocol="REST", raw_response=self.bounded_payload(json.dumps(data, indent=2)), source_mapping={"municipal_id":"municipal_id","resident_name":"resident_name","ward":"ward","address":"address","registration_status":"registration_status"})
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("municipality_http_error status=%s", status)
            if status == 404:
                return ConnectorResult("municipality", "not_found", {}, "Municipality record was not found")
            return ConnectorResult("municipality", "failed", {}, "Municipality service returned an error")
        except httpx.TimeoutException:
            logger.warning("municipality_timeout")
            return ConnectorResult("municipality", "timeout", {}, "Municipality service timed out")
        except httpx.RequestError:
            logger.warning("municipality_unavailable")
            return ConnectorResult("municipality", "unavailable", {}, "Municipality service could not be reached")
        except (KeyError, TypeError, ValueError):
            logger.warning("municipality_invalid_response")
            return ConnectorResult("municipality", "invalid_response", {}, "Municipality service returned an invalid response")
