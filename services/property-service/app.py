from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from typing import Literal
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request, Response
from pydantic import BaseModel

SERVICES_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVICES_ROOT))
from seed_loader import load_seed_records  # noqa: E402

app = FastAPI(title="Property Service (Simulated SOAP)")


class PropertyData(BaseModel):
    citizenId: str
    ownerName: str
    propertyId: str
    propertyAddress: str
    propertyType: str
    ownershipStatus: Literal["ACTIVE", "INACTIVE"]


RECORDS = load_seed_records(
    SERVICES_ROOT / "seed" / "property.json", PropertyData, id_field="citizenId"
)


def soap_fault(message: str, status_code: int) -> Response:
    body = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body><soap:Fault><faultcode>soap:Client</faultcode>
  <faultstring>{escape(message)}</faultstring></soap:Fault></soap:Body>
</soap:Envelope>"""
    return Response(content=body, media_type="text/xml", status_code=status_code)


@app.get("/health")
def health():
    return {"status": "ok", "service": "property-soap"}


@app.post("/soap/property")
async def get_property_soap(request: Request):
    try:
        root = ET.fromstring(await request.body())
    except ET.ParseError:
        return soap_fault("Invalid SOAP XML", 400)

    citizen_id = next(
        ((node.text or "").strip().upper() for node in root.iter()
         if node.tag.split("}")[-1] == "citizenId"),
        "",
    )
    record = RECORDS.get(citizen_id)
    if record is None:
        return soap_fault("Property record not found", 404)

    data = record.model_dump()
    response_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body><GetPropertyDetailsResponse>
    <citizenId>{escape(data['citizenId'])}</citizenId>
    <ownerName>{escape(data['ownerName'])}</ownerName>
    <propertyId>{escape(data['propertyId'])}</propertyId>
    <propertyAddress>{escape(data['propertyAddress'])}</propertyAddress>
    <propertyType>{escape(data['propertyType'])}</propertyType>
    <ownershipStatus>{escape(data['ownershipStatus'])}</ownershipStatus>
  </GetPropertyDetailsResponse></soap:Body>
</soap:Envelope>"""
    return Response(content=response_xml, media_type="text/xml")
