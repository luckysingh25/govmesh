import httpx
import pytest

from app.api.endpoints.systems import check_department_health


@pytest.mark.asyncio
async def test_health_check_reports_online_for_healthy_response():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"status": "healthy"}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await check_department_health(client, "identity", "Identity Service", "http://identity", "REST")

    assert result["status"] == "Online"
    assert result["latency_ms"] >= 0
    assert result["uptime_percent"] is None
    assert result["error_rate"] is None


@pytest.mark.asyncio
async def test_health_check_reports_degraded_for_bad_response():
    transport = httpx.MockTransport(lambda request: httpx.Response(503, json={"status": "unhealthy"}))
    async with httpx.AsyncClient(transport=transport) as client:
        result = await check_department_health(client, "tax", "Tax Service", "http://tax", "REST")

    assert result["status"] == "Degraded"


@pytest.mark.asyncio
async def test_health_check_reports_offline_for_timeout():
    def timeout(_request):
        raise httpx.ReadTimeout("timed out")

    async with httpx.AsyncClient(transport=httpx.MockTransport(timeout)) as client:
        result = await check_department_health(client, "property", "Property Service", "http://property", "SOAP")

    assert result["status"] == "Offline"
