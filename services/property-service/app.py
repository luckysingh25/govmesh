from pathlib import Path
import sys
import os
import xml.etree.ElementTree as ET
from typing import Literal
from xml.sax.saxutils import escape

from fastapi import FastAPI, Request, Response, Header, HTTPException
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
DEMO_STATE = {"schema_version": 1, "available": True}


def require_demo_control(key: str | None) -> None:
    expected = os.environ.get("DEMO_CONTROL_KEY")
    if os.environ.get("DEMO_CONTROLS_ENABLED", "false").casefold() != "true" or not expected or key != expected:
        raise HTTPException(status_code=404, detail="Not found")


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
    if not DEMO_STATE["available"]:
        return soap_fault("Property service temporarily unavailable", 503)
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
    owner_tag = "ownerName" if DEMO_STATE["schema_version"] == 1 else "propertyOwnerName"
    response_xml = f"""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body><GetPropertyDetailsResponse>
    <citizenId>{escape(data['citizenId'])}</citizenId>
    <{owner_tag}>{escape(data['ownerName'])}</{owner_tag}>
    <propertyId>{escape(data['propertyId'])}</propertyId>
    <propertyAddress>{escape(data['propertyAddress'])}</propertyAddress>
    <propertyType>{escape(data['propertyType'])}</propertyType>
    <ownershipStatus>{escape(data['ownershipStatus'])}</ownershipStatus>
  </GetPropertyDetailsResponse></soap:Body>
</soap:Envelope>"""
    headers = {"X-Schema-Version": str(DEMO_STATE["schema_version"])}
    correlation_id = request.headers.get("X-Correlation-ID")
    if correlation_id:
        headers["X-Correlation-ID"] = correlation_id
    return Response(content=response_xml, media_type="text/xml", headers=headers)


@app.put("/demo/schema/{version}")
def set_schema(version: int, x_demo_control_key: str | None = Header(None)):
    require_demo_control(x_demo_control_key)
    if version not in {1, 2}:
        raise HTTPException(status_code=422, detail="Supported schema versions are 1 and 2")
    DEMO_STATE["schema_version"] = version
    return dict(DEMO_STATE)


@app.put("/demo/availability/{available}")
def set_availability(available: bool, x_demo_control_key: str | None = Header(None)):
    require_demo_control(x_demo_control_key)
    DEMO_STATE["available"] = available
    return dict(DEMO_STATE)


@app.post("/demo/reset")
def reset_demo(x_demo_control_key: str | None = Header(None)):
    require_demo_control(x_demo_control_key)
    DEMO_STATE.update(schema_version=1, available=True)
    return dict(DEMO_STATE)
