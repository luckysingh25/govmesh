"""Tests for the consent-management and policy-validation layer.

Uses the same in-memory SQLite + monkeypatching approach as the existing
test_service_request_slice.py so the tests stay fast, isolated, and don't
require a running Postgres or department services.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.application.service_request_service import ServiceRequestService
from app.connectors.base import ConnectorResult
from app.db.session import Base, get_db
from app.models.workflow import WorkflowDefinition
from app.main import app


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine)
Base.metadata.create_all(test_engine)


def override_db():
    db = TestSession()
    # Seed workflow definitions if not present
    if not db.query(WorkflowDefinition).filter_by(name="business_registration").first():
        db.add(WorkflowDefinition(
            name="business_registration",
            description="Test workflow",
            steps=["identity", "property", "municipality", "tax"],
        ))
        db.commit()
    try:
        yield db
    finally:
        db.close()


async def successful_departments(_self, db, citizen_id, request_id):
    return [
        ConnectorResult("identity", "success", {"full_name": "Rajesh Kumar", "address": "123 MG Road"}),
        ConnectorResult("property", "success", {"property_id": "PROP-1"}),
        ConnectorResult("municipality", "success", {"resident_name": "Rajesh Kumar", "address": "123 MG Road"}),
        ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    ]


# ---------------------------------------------------------------------------
# Consent API CRUD
# ---------------------------------------------------------------------------

def test_grant_consent_returns_record():
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.post("/api/v1/consent", json={
        "citizen_id": "CIT-1001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })
    assert resp.status_code == 201
    body = resp.json()
    assert body["citizen_id"] == "CIT-1001"
    assert "identity" in body["departments"]
    assert body["revoked_at"] is None
    app.dependency_overrides.clear()


def test_get_active_consent():
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    # Grant first
    client.post("/api/v1/consent", json={
        "citizen_id": "CIT-2001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })

    resp = client.get("/api/v1/consent/CIT-2001/business_registration")
    assert resp.status_code == 200
    assert resp.json()["citizen_id"] == "CIT-2001"
    app.dependency_overrides.clear()


def test_get_active_consent_returns_404_when_none():
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    resp = client.get("/api/v1/consent/NOONE/business_registration")
    assert resp.status_code == 404
    app.dependency_overrides.clear()


def test_revoke_consent():
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    grant = client.post("/api/v1/consent", json={
        "citizen_id": "CIT-3001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })
    consent_id = grant.json()["id"]

    resp = client.delete(f"/api/v1/consent/{consent_id}")
    assert resp.status_code == 200
    assert resp.json()["message"] == "Consent revoked successfully"

    # Active consent should now be gone
    resp2 = client.get("/api/v1/consent/CIT-3001/business_registration")
    assert resp2.status_code == 404
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Policy enforcement in the service-request flow
# ---------------------------------------------------------------------------

def test_service_request_denied_without_consent(monkeypatch):
    """A service-request without prior consent should be denied."""
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(ServiceRequestService, "fetch_department_results", successful_departments)
    client = TestClient(app)

    resp = client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-NOCONSENT",
        "service_type": "business_registration",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] == "denied"
    assert body["identity"]["status"] == "denied"
    assert body["property"]["status"] == "denied"
    assert body["policy_decision"] is not None
    assert "No active consent" in body["policy_decision"]
    app.dependency_overrides.clear()


def test_service_request_allowed_with_consent(monkeypatch):
    """After granting consent, the request should proceed normally."""
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr("app.application.workflow_engine.redis_available", lambda: False)
    monkeypatch.setattr("app.application.service_request_service.redis_available", lambda: False)

    # Mock all connectors to succeed via CONNECTOR_MAP
    from unittest.mock import MagicMock, AsyncMock
    from app.connectors.base import ConnectorResult
    mock_results = {
        "identity": ConnectorResult("identity", "success", {"full_name": "Rajesh Kumar", "address": "123 MG Road"}),
        "property": ConnectorResult("property", "success", {"property_id": "PROP-1"}),
        "municipality": ConnectorResult("municipality", "success", {"resident_name": "Rajesh Kumar", "address": "123 MG Road"}),
        "tax": ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    }
    mock_map = {
        dept: MagicMock(return_value=MagicMock(
            fetch_data=AsyncMock(return_value=result),
            close=AsyncMock(),
        ))
        for dept, result in mock_results.items()
    }
    monkeypatch.setattr("app.application.workflow_engine.CONNECTOR_MAP", mock_map)

    client = TestClient(app)

    # Grant consent
    client.post("/api/v1/consent", json={
        "citizen_id": "CIT-5001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })

    # Now submit service request
    resp = client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-5001",
        "service_type": "business_registration",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] in ("completed", "success")
    assert body["consent_id"] is not None
    assert "allowed" in body["policy_decision"].lower()
    assert body["workflow_id"] is not None
    app.dependency_overrides.clear()


def test_service_request_denied_after_revocation(monkeypatch):
    """Revoking consent should cause subsequent requests to be denied."""
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(ServiceRequestService, "fetch_department_results", successful_departments)
    client = TestClient(app)

    # Grant
    grant = client.post("/api/v1/consent", json={
        "citizen_id": "CIT-6001",
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })
    consent_id = grant.json()["id"]

    # Revoke
    client.delete(f"/api/v1/consent/{consent_id}")

    # Request should be denied
    resp = client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-6001",
        "service_type": "business_registration",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] == "denied"
    app.dependency_overrides.clear()


def test_partial_consent_is_denied(monkeypatch):
    """Consent that doesn't cover all four departments should be denied."""
    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(ServiceRequestService, "fetch_department_results", successful_departments)
    client = TestClient(app)

    # Grant consent for only 2 departments
    client.post("/api/v1/consent", json={
        "citizen_id": "CIT-7001",
        "service_type": "business_registration",
        "departments": ["identity", "tax"],
    })

    resp = client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-7001",
        "service_type": "business_registration",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["overall_status"] == "denied"
    assert "does not cover" in body["policy_decision"]
    app.dependency_overrides.clear()
