from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import create_access_token, get_password_hash
from app.core.config import settings
from app.db.seed_workflows import seed_workflow_definitions
from app.db.session import Base, get_db
from app.main import app
from app.models.service_request import ServiceRequest
from app.models.consent import CitizenConsent
from app.models.user import User
from app.models.workflow import WorkflowDefinition, WorkflowInstance


@pytest.fixture
def secure_client():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with Session() as db:
        seed_workflow_definitions(db)

    def override_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    def headers(email: str, role: str, citizen_id: str | None = None):
        with Session() as db:
            db.add(User(email=email, hashed_password=get_password_hash("test-password-only"), role=role, citizen_id=citizen_id))
            db.commit()
        token = create_access_token({"sub": email, "role": role})
        return {"Authorization": f"Bearer {token}"}

    yield client, Session, headers
    app.dependency_overrides.clear()
    engine.dispose()


def test_legacy_demo_token_is_rejected_without_creating_an_admin(secure_client):
    client, Session, _ = secure_client
    response = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer demo-admin-token"})
    assert response.status_code == 401
    with Session() as db:
        assert db.query(User).count() == 0


def test_public_registration_cannot_create_a_privileged_user(secure_client):
    client, Session, _ = secure_client
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "public-user@govmesh.example", "password": "registration-only", "role": "admin"},
    )
    assert response.status_code == 422
    with Session() as db:
        assert db.query(User).filter_by(email="public-user@govmesh.example").first() is None


def test_citizen_cannot_read_or_revoke_another_citizens_consent(secure_client):
    client, _, headers = secure_client
    owner = headers("owner@test.local", "citizen", "CIT-1001")
    other = headers("other@test.local", "citizen", "CIT-1002")
    grant = client.post("/api/v1/consent", headers=owner, json={"citizen_id":"CIT-1001","service_type":"tax_clearance","departments":["identity","tax"]})
    assert grant.status_code == 201
    consent_id = grant.json()["id"]
    assert client.get("/api/v1/consent/CIT-1001/tax_clearance", headers=other).status_code == 403
    assert client.delete(f"/api/v1/consent/{consent_id}", headers=other).status_code == 403


def test_denied_request_and_manual_start_make_zero_connector_calls(secure_client, monkeypatch):
    client, Session, headers = secure_client
    citizen = headers("denied@test.local", "citizen", "CIT-1003")
    factory = MagicMock()
    monkeypatch.setattr("app.application.workflow_engine.CONNECTOR_MAP", {name: factory for name in ("identity","property","municipality","tax")})
    denied = client.post("/api/v1/service-requests", headers=citizen, json={"citizen_id":"CIT-1003","service_type":"business_registration"})
    assert denied.status_code == 200
    assert denied.json()["overall_status"] == "denied"
    assert factory.call_count == 0
    manual = client.post("/api/v1/workflows/start", headers=citizen, json={"service_request_id":denied.json()["request_id"]})
    assert manual.status_code == 403
    assert factory.call_count == 0


def test_demo_controls_require_role_explicit_flag_and_demo_environment(secure_client):
    client, _, headers = secure_client
    citizen = headers("demo-citizen@test.local", "citizen", "CIT-1004")
    steward = headers("demo-steward@test.local", "data_steward")
    original = (settings.environment, settings.demo_controls_enabled, settings.demo_control_key)
    try:
        settings.environment = "demo"
        settings.demo_controls_enabled = True
        settings.demo_control_key = "test-only-key"
        assert client.post("/api/v1/intelligence/demo/trigger", headers=citizen).status_code == 403
        settings.demo_controls_enabled = False
        assert client.post("/api/v1/intelligence/demo/trigger", headers=steward).status_code == 404
        settings.demo_controls_enabled = True
        settings.environment = "production"
        assert client.post("/api/v1/intelligence/demo/trigger", headers=steward).status_code == 404
    finally:
        settings.environment, settings.demo_controls_enabled, settings.demo_control_key = original


@pytest.mark.parametrize("consent_state", ["revoked", "expired"])
def test_revoked_or_expired_consent_prevents_resume(secure_client, monkeypatch, consent_state):
    client, Session, headers = secure_client
    citizen_headers = headers(f"resume-{consent_state}@govmesh.example", "citizen", "CIT-1001")
    request_id = f"REQ-{consent_state.upper()}"
    with Session() as db:
        definition = db.query(WorkflowDefinition).filter_by(name="business_registration").one()
        consent = CitizenConsent(
            citizen_id="CIT-1001",
            service_type="business_registration",
            departments=["identity", "property", "municipality", "tax"],
            expires_at=(
                datetime.now(timezone.utc) - timedelta(minutes=1)
                if consent_state == "expired"
                else datetime.now(timezone.utc) + timedelta(hours=1)
            ),
            revoked_at=datetime.now(timezone.utc) if consent_state == "revoked" else None,
        )
        db.add_all([
            consent,
            ServiceRequest(
                request_id=request_id,
                citizen_id="CIT-1001",
                service_type="business_registration",
                correlation_id=f"corr-{consent_state}",
                status="partially_completed",
            ),
            WorkflowInstance(
                workflow_id=f"workflow-{consent_state}",
                definition_id=definition.id,
                service_request_id=request_id,
                citizen_id="CIT-1001",
                status="partially_completed",
            ),
        ])
        db.commit()

    resume = AsyncMock()
    monkeypatch.setattr("app.api.endpoints.workflows._engine.resume_or_retry", resume)
    response = client.post(f"/api/v1/workflows/by-request/{request_id}/resume", headers=citizen_headers)
    assert response.status_code == 403
    resume.assert_not_awaited()
