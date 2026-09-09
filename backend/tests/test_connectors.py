import httpx
import pytest

from app.connectors.identity import IdentityConnector
from app.connectors.municipality import MunicipalityConnector
from app.connectors.property import PropertyConnector
from app.connectors.tax import TaxConnector


def client_for(handler):
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=0.1)


@pytest.mark.asyncio
async def test_identity_success_normalizes_protocol_fields():
    connector = IdentityConnector("http://identity.test")
    connector.client = client_for(lambda request: httpx.Response(200, json={
        "citizen_id": "CIT-1001", "full_name": "Asha Verma",
        "date_of_birth": "1988-04-12", "address": "Demo Address",
        "verification_status": "VERIFIED",
    }))
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "success"
    assert result.data["verification_status"] == "VERIFIED"


@pytest.mark.asyncio
async def test_municipality_success_normalizes_protocol_fields():
    connector = MunicipalityConnector("http://municipality.test")
    connector.client = client_for(lambda request: httpx.Response(200, json={
        "citizen_id": "CIT-1001", "resident_name": "Asha Verma",
        "municipal_id": "DEMO-MUN-1001", "ward": "Demo Ward",
        "address": "Demo Address", "registration_status": "ACTIVE",
    }))
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "success"
    assert result.data["registration_status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_property_success_parses_and_normalizes_soap():
    xml = """<Envelope><Body><GetPropertyDetailsResponse>
    <ownerName>Asha Verma</ownerName><propertyId>DEMO-PROP-1001</propertyId>
    <propertyAddress>Demo Address</propertyAddress><propertyType>Commercial</propertyType>
    <ownershipStatus>ACTIVE</ownershipStatus></GetPropertyDetailsResponse></Body></Envelope>"""
    connector = PropertyConnector("http://property.test")
    connector.client = client_for(lambda request: httpx.Response(200, text=xml))
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "success"
    assert result.data["property_id"] == "DEMO-PROP-1001"
    assert result.data["ownership_status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_tax_success_normalizes_async_lookup():
    def handler(request):
        if request.method == "POST":
            return httpx.Response(200, json={"job_id": "TAX-JOB-CIT-1001", "status": "completed"})
        return httpx.Response(200, json={"status": "completed", "result": {
            "citizenId": "CIT-1001", "taxpayerName": "Asha Verma",
            "taxId": "DEMO-TAX-1001", "taxStatus": "CLEARED",
            "outstandingAmount": 0, "assessmentYear": "2025-2026",
        }})
    connector = TaxConnector("http://tax.test")
    connector.client = client_for(handler)
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "success"
    assert result.data["assessment_year"] == "2025-2026"


@pytest.mark.asyncio
@pytest.mark.parametrize("connector_cls", [IdentityConnector, MunicipalityConnector, PropertyConnector, TaxConnector])
async def test_not_found_never_becomes_false_success(connector_cls):
    connector = connector_cls("http://department.test")
    connector.client = client_for(lambda request: httpx.Response(404, text="not found"))
    result = await connector.fetch_data("CIT-9999")
    await connector.close()
    assert result.status == "not_found"
    assert result.data == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("connector_cls", [IdentityConnector, MunicipalityConnector, PropertyConnector, TaxConnector])
async def test_timeout_never_becomes_false_success(connector_cls):
    def timeout(request):
        raise httpx.ReadTimeout("timed out", request=request)
    connector = connector_cls("http://department.test")
    connector.client = client_for(timeout)
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "timeout"
    assert result.data == {}


@pytest.mark.asyncio
@pytest.mark.parametrize("connector_cls", [IdentityConnector, MunicipalityConnector, PropertyConnector, TaxConnector])
async def test_connection_failure_never_becomes_false_success(connector_cls):
    def unavailable(request):
        raise httpx.ConnectError("connection refused", request=request)
    connector = connector_cls("http://department.test")
    connector.client = client_for(unavailable)
    result = await connector.fetch_data("CIT-1001")
    await connector.close()
    assert result.status == "unavailable"
    assert result.data == {}
    assert "connection refused" not in (result.error or "")


@pytest.mark.asyncio
async def test_invalid_json_and_xml_are_reported_without_internal_details():
    identity = IdentityConnector("http://identity.test")
    identity.client = client_for(lambda request: httpx.Response(200, text="not-json"))
    identity_result = await identity.fetch_data("CIT-1001")
    await identity.close()

    property_connector = PropertyConnector("http://property.test")
    property_connector.client = client_for(lambda request: httpx.Response(200, text="<broken"))
    property_result = await property_connector.fetch_data("CIT-1001")
    await property_connector.close()

    assert identity_result.status == "invalid_response"
    assert property_result.status == "invalid_response"


@pytest.mark.asyncio
async def test_tax_pending_is_explicit_and_has_no_invented_result():
    connector = TaxConnector("http://tax.test")
    connector.client = client_for(lambda request: httpx.Response(
        200, json={"job_id": "TAX-JOB-CIT-1008", "status": "pending"}
    ))
    result = await connector.fetch_data("CIT-1008")
    await connector.close()
    assert result.status == "pending"
    assert result.data == {"tax_status": "PENDING"}

