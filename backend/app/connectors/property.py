import logging
import xml.etree.ElementTree as ET
from app.connectors.base import BaseConnector, ConnectorResult
import httpx

logger = logging.getLogger(__name__)

from app.core.config import settings

class PropertyConnector(BaseConnector):
    def __init__(self, base_url: str = None):
        super().__init__(base_url or settings.property_url)

    async def fetch_data(self, citizen_id: str) -> ConnectorResult:
        try:
            # Simulate a SOAP payload
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
            
            # Parse XML
            root = ET.fromstring(response.text)
            
            # Simple simulation of XML extraction
            data = {}
            for child in root.iter():
                # Ignore soap namespaces for simplicity in this MVP
                tag_name = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if tag_name in ["ownerName", "propertyId", "propertyAddress", "propertyType"]:
                    data[tag_name] = child.text
                    
            if not data:
                return ConnectorResult("property", "failed", {}, "Property not found or invalid XML response")
                
            return ConnectorResult("property", "success", {
                "property_id": data.get("propertyId"),
                "owner_name": data.get("ownerName"),
                "address": data.get("propertyAddress"),
                "property_type": data.get("propertyType"),
            })
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Property API HTTP error: {e}")
            return ConnectorResult("property", "failed", {}, f"HTTP Error {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Property API Request error: {e}")
            return ConnectorResult("property", "failed", {}, "Property service unavailable")
        except ET.ParseError as e:
            logger.error(f"Property API XML parsing error: {e}")
            return ConnectorResult("property", "failed", {}, "Invalid XML format received")
        except Exception as e:
            logger.exception("Unexpected error in PropertyConnector")
            return ConnectorResult("property", "failed", {}, str(e))
