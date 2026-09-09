import httpx
import logging
import xml.etree.ElementTree as ET

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class PropertyConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.property_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            soap_payload = f"""<?xml version="1.0" encoding="utf-8"?>
            <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
              <soap:Body>
                <GetPropertyDetailsRequest>
                  <citizenId>{citizen_id}</citizenId>
                </GetPropertyDetailsRequest>
              </soap:Body>
            </soap:Envelope>"""
            
            headers = {"Content-Type": "text/xml; charset=utf-8"}
            response = await self.client.post(f"{self.base_url}/soap/property", data=soap_payload, headers=headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            data = {}
            for child in root.iter():
                tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag_name in ["ownerName", "propertyId", "propertyAddress", "propertyType", "ownershipStatus"]:
                    data[tag_name] = child.text
            required = {"ownerName", "propertyId", "propertyAddress", "propertyType", "ownershipStatus"}
            if not required.issubset(data) or any(not data[key] for key in required):
                return ConnectorResult("property", "invalid_response", {}, "Property service returned an invalid response")
            return ConnectorResult("property", "success", {
                "property_id": data.get("propertyId"),
                "owner_name": data.get("ownerName"),
                "address": data.get("propertyAddress"),
                "property_type": data.get("propertyType"),
                "ownership_status": data.get("ownershipStatus"),
            })
        except httpx.HTTPStatusError as exc:
            status = exc.response.status_code
            logger.warning("property_http_error status=%s", status)
            if status == 404:
                return ConnectorResult("property", "not_found", {}, "Property record was not found")
            return ConnectorResult("property", "failed", {}, "Property service returned an error")
        except httpx.TimeoutException:
            logger.warning("property_timeout")
            return ConnectorResult("property", "timeout", {}, "Property service timed out")
        except httpx.RequestError:
            logger.warning("property_unavailable")
            return ConnectorResult("property", "unavailable", {}, "Property service could not be reached")
        except ET.ParseError:
            logger.warning("property_invalid_xml")
            return ConnectorResult("property", "invalid_response", {}, "Property service returned invalid XML")
