import importlib.util
from pathlib import Path

import httpx
import pytest

from app.connectors.identity import IdentityConnector
from app.connectors.municipality import MunicipalityConnector
from app.connectors.property import PropertyConnector
from app.connectors.tax import TaxConnector


ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def load_app(name: str, relative: str):
    return load_module(name, relative).app


class CaptureTransport(httpx.AsyncBaseTransport):
    def __init__(self, app):
        self.inner = httpx.ASGITransport(app=app)
        self.requests = []

    async def handle_async_request(self, request):
        self.requests.append(request)
        return await self.inner.handle_async_request(request)

    async def aclose(self):
        await self.inner.aclose()


@pytest.mark.asyncio
async def test_real_department_apps_protocols_and_correlation_propagation():
    correlation = "integration-correlation-001"
    cases = [
        (IdentityConnector, "services/identity-service/app.py", "identity"),
        (MunicipalityConnector, "services/municipality-service/app.py", "municipality"),
        (PropertyConnector, "services/property-service/app.py", "property"),
        (TaxConnector, "services/tax-service/app.py", "tax"),
    ]
    for connector_type, source, department in cases:
        transport = CaptureTransport(load_app(f"integration_{department}", source))
        connector = connector_type("http://department.test")
        connector.client = httpx.AsyncClient(transport=transport, base_url="http://department.test")
        result = await connector.fetch_data("CIT-1001", correlation)
        await connector.close()
        assert result.status == "success"
        assert result.department == department
        assert result.raw_response
        assert result.source_mapping
        assert transport.requests[0].headers["x-correlation-id"] == correlation


@pytest.mark.asyncio
async def test_real_tax_job_preserves_id_and_transitions_to_completed():
    app = load_app("integration_tax_pending", "services/tax-service/app.py")
    connector = TaxConnector("http://tax.test")
    connector.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://tax.test")
    pending = await connector.fetch_data("CIT-1008", "corr-tax")
    processing = await connector.resume_job(pending.external_job_id, "corr-tax")
    completed = await connector.resume_job(pending.external_job_id, "corr-tax")
    await connector.close()
    assert [pending.status, processing.status, completed.status] == ["pending", "processing", "success"]
    assert pending.external_job_id == processing.external_job_id == completed.external_job_id
    assert completed.data["tax_status"] == "CLEARED"


@pytest.mark.asyncio
async def test_real_property_v2_fails_then_uses_constrained_approved_mapping():
    module = load_module("integration_property_v2", "services/property-service/app.py")
    module.DEMO_STATE["schema_version"] = 2
    transport = httpx.ASGITransport(app=module.app)

    incompatible = PropertyConnector("http://property.test")
    incompatible.client = httpx.AsyncClient(transport=transport, base_url="http://property.test")
    before = await incompatible.fetch_data("CIT-1001", "corr-property")
    await incompatible.close()
    assert before.status == "schema_incompatible"
    assert "propertyOwnerName" in before.raw_response

    recovered = PropertyConnector(
        "http://property.test",
        approved_mapping={"propertyOwnerName": "property.owner_name"},
        mapping_version=1,
    )
    recovered.client = httpx.AsyncClient(transport=httpx.ASGITransport(app=module.app), base_url="http://property.test")
    after = await recovered.fetch_data("CIT-1001", "corr-property-2")
    await recovered.close()
    assert after.status == "success"
    assert after.data["owner_name"]
    assert after.schema_version == 2
    assert after.mapping_version == 1
