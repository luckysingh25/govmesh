import httpx
import logging
import xml.etree.ElementTree as ET

from app.connectors.base import BaseConnector, ConnectorResult
from app.core.config import settings

logger = logging.getLogger(__name__)

class PropertyConnector(BaseConnector):
    def __init__(self, base_url: str = None, approved_mapping: dict | None = None, mapping_version: int | None = None):
        super().__init__(base_url or settings.property_url)
        self.approved_mapping = approved_mapping or {}
        self.mapping_version = mapping_version

    async def fetch_data(self, citizen_id: str, correlation_id: str | None = None) -> ConnectorResult:
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
            if correlation_id:
                headers["X-Correlation-ID"] = correlation_id
            response = await self.client.post(f"{self.base_url}/soap/property", data=soap_payload, headers=headers)
            response.raise_for_status()
            
            root = ET.fromstring(response.text)
            data = {}
            for child in root.iter():
                tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag_name in ["ownerName", "propertyOwnerName", "propertyId", "propertyAddress", "propertyType", "ownershipStatus"]:
                    data[tag_name] = child.text
            owner_field = "ownerName"
            schema_version = int(response.headers.get("X-Schema-Version", "1"))
            if schema_version == 2:
                owner_field = next((source for source, target in self.approved_mapping.items() if target == "property.owner_name"), "ownerName")
            required = {owner_field, "propertyId", "propertyAddress", "propertyType", "ownershipStatus"}
            if not required.issubset(data) or any(not data[key] for key in required):
                return ConnectorResult("property", "schema_incompatible", {}, "Property schema is incompatible; an approved owner-name mapping is required", protocol="SOAP/XML", raw_response=self.bounded_payload(response.text), schema_version=schema_version)
            normalized = {
                "property_id": data.get("propertyId"),
                "owner_name": data.get(owner_field),
                "address": data.get("propertyAddress"),
                "property_type": data.get("propertyType"),
                "ownership_status": data.get("ownershipStatus"),
            }
            mapping = {"propertyId":"property.property_id", owner_field:"property.owner_name", "propertyAddress":"property.address", "propertyType":"property.property_type", "ownershipStatus":"property.ownership_status"}
            return ConnectorResult("property", "success", normalized, protocol="SOAP/XML", raw_response=self.bounded_payload(response.text), source_mapping=mapping, schema_version=schema_version, mapping_version=self.mapping_version if schema_version == 2 else None)
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
