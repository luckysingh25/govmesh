from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.application.service_request_service import ServiceRequestService, overall_status
from app.application.workflow_engine import WorkflowEngine
from app.connectors.base import ConnectorResult
from app.db.session import Base, get_db
from app.models.workflow import WorkflowDefinition
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


def test_create_request_returns_unified_response_and_correlation_id(monkeypatch):
    app.dependency_overrides[get_db] = override_db
    # Patch redis_available to force sync execution
    monkeypatch.setattr("app.application.workflow_engine.redis_available", lambda: False)
    monkeypatch.setattr("app.application.service_request_service.redis_available", lambda: False)

    # Mock all connectors to succeed via CONNECTOR_MAP
    from unittest.mock import MagicMock, AsyncMock
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
    assert body["overall_status"] in ("completed", "success")
    assert body["consent_id"] is not None
    assert body["workflow_id"] is not None
    app.dependency_overrides.clear()


def test_partial_department_failure_is_degraded_not_fatal():
    results = [
        ConnectorResult("identity", "success", {"full_name": "Rajesh Kumar"}),
        ConnectorResult("property", "failed", {}, "Property service unavailable"),
        ConnectorResult("municipality", "success", {"ward": "Ward 72"}),
        ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    ]

    assert overall_status(results) == "partially_completed"
