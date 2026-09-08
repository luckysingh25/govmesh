from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.application.service_request_service import ServiceRequestService, overall_status
from app.connectors.base import ConnectorResult
from app.db.session import Base, get_db
from app.main import app


test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine)
Base.metadata.create_all(test_engine)


def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


async def successful_departments(_self, db, citizen_id, request_id):
    return [
        ConnectorResult(
            "identity",
            "success",
            {
                "full_name": "Rajesh Kumar",
                "date_of_birth": "1985-06-15",
                "address": "123 MG Road",
            },
        ),
        ConnectorResult(
            "property",
            "success",
            {
                "property_id": "PROP-1",
                "owner_name": "Rajesh Kumar",
                "address": "123 MG Road",
                "property_type": "Commercial",
            },
        ),
        ConnectorResult(
            "municipality",
            "success",
            {
                "municipal_id": "MUN-1",
                "resident_name": "Rajesh Kumar",
                "address": "123 MG Road",
            },
        ),
        ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    ]


def test_create_request_returns_unified_response_and_correlation_id(monkeypatch):
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(ServiceRequestService, "fetch_department_results", successful_departments)
    client = TestClient(app)

    # Grant consent first (required by the policy gate)
    client.post("/api/v1/consent", json={
        "citizen_id": "CIT-1001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })

    response = client.post(
        "/api/v1/service-requests",
        headers={"X-Correlation-ID": "demo-correlation-123"},
        json={"citizen_id": "CIT-1001", "service_type": "business_registration"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["correlation_id"] == "demo-correlation-123"
    assert response.headers["X-Correlation-ID"] == "demo-correlation-123"
    assert body["citizen"]["name"] == "Rajesh Kumar"
    assert body["identity"]["status"] == "success"
    assert body["overall_status"] == "completed"
    assert body["consent_id"] is not None
    assert body["insights"] == []
    app.dependency_overrides.clear()


def test_create_request_includes_post_aggregation_insights(monkeypatch):
    async def departments_with_tax_due(_self, db, citizen_id, request_id):
        results = await successful_departments(_self, db, citizen_id, request_id)
        results[-1].data["tax_status"] = "DUE"
        return results

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        ServiceRequestService, "fetch_department_results", departments_with_tax_due
    )
    client = TestClient(app)
    client.post("/api/v1/consent", json={
        "citizen_id": "CIT-INTELLIGENCE",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })

    response = client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-INTELLIGENCE",
        "service_type": "business_registration",
    })

    assert response.status_code == 200
    assert [item["rule_id"] for item in response.json()["insights"]] == [
        "TAX_CLEARANCE_NOT_CONFIRMED"
    ]
    app.dependency_overrides.clear()


def test_partial_department_failure_is_degraded_not_fatal():
    results = [
        ConnectorResult("identity", "success", {"full_name": "Rajesh Kumar"}),
        ConnectorResult("property", "failed", {}, "Property service unavailable"),
        ConnectorResult("municipality", "success", {"ward": "Ward 72"}),
        ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    ]

    assert overall_status(results) == "partially_completed"
