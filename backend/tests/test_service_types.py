from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.connectors.base import ConnectorResult
from app.core.service_types import WORKFLOW_DEFINITIONS, required_departments
from app.db.seed_workflows import seed_workflow_definitions
from app.db.session import Base, get_db
from app.main import app
from app.models.workflow import WorkflowDefinition, WorkflowInstance


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    with factory() as db:
        seed_workflow_definitions(db)
    yield factory
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(session_factory):
    def override_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def connector_map(monkeypatch):
    results = {
        "identity": ConnectorResult("identity", "success", {
            "full_name": "Demo Citizen", "date_of_birth": "1990-01-01",
            "address": "Demo Address", "verification_status": "VERIFIED",
        }),
        "property": ConnectorResult("property", "success", {
            "property_id": "DEMO-PROP", "owner_name": "Demo Citizen",
            "address": "Demo Address", "property_type": "Residential",
            "ownership_status": "ACTIVE",
        }),
        "municipality": ConnectorResult("municipality", "success", {
            "municipal_id": "DEMO-MUN", "resident_name": "Demo Citizen",
            "address": "Demo Address", "ward": "Demo Ward",
            "registration_status": "ACTIVE",
        }),
        "tax": ConnectorResult("tax", "success", {
            "tax_id": "DEMO-TAX", "taxpayer_name": "Demo Citizen",
            "tax_status": "CLEARED", "outstanding_amount": 0,
            "assessment_year": "2025-2026",
        }),
    }
    mocked = {
        name: MagicMock(return_value=MagicMock(
            fetch_data=AsyncMock(return_value=result), close=AsyncMock()
        ))
        for name, result in results.items()
    }
    monkeypatch.setattr("app.application.workflow_engine.CONNECTOR_MAP", mocked)
    return mocked


def test_workflow_seed_is_idempotent_and_matches_canonical_mapping(session_factory):
    with session_factory() as db:
        seed_workflow_definitions(db)
        seed_workflow_definitions(db)
        definitions = db.query(WorkflowDefinition).all()
        assert len(definitions) == len(WORKFLOW_DEFINITIONS)
        assert {item.name: item.steps for item in definitions} == {
            name: definition["steps"] for name, definition in WORKFLOW_DEFINITIONS.items()
        }


@pytest.mark.parametrize(
    ("citizen_id", "service_type"),
    [
        ("CIT-9101", "business_registration"),
        ("CIT-9102", "property_transfer"),
        ("CIT-9103", "tax_clearance"),
    ],
)
def test_each_service_uses_matching_workflow_and_consent(
    client, session_factory, connector_map, citizen_id, service_type
):
    departments = list(required_departments(service_type))
    consent = client.post("/api/v1/consent", json={
        "citizen_id": citizen_id,
        "service_type": service_type,
        "departments": departments,
    })
    assert consent.status_code == 201

    response = client.post("/api/v1/service-requests", json={
        "citizen_id": citizen_id, "service_type": service_type,
    })
    assert response.status_code == 200
    body = response.json()
    assert body["overall_status"] == "success"
    assert body["insights"] == []
    for department in set(WORKFLOW_DEFINITIONS[service_type]["steps"]):
        assert body[department]["status"] == "success"
    for department in {"identity", "property", "municipality", "tax"} - set(departments):
        assert body[department]["status"] == "not_required"

    with session_factory() as db:
        workflow = db.query(WorkflowInstance).filter_by(workflow_id=body["workflow_id"]).one()
        assert workflow.definition.name == service_type
        assert [step.step_name for step in workflow.steps] == departments


def test_unsupported_service_type_and_invalid_citizen_are_rejected(client):
    assert client.post("/api/v1/service-requests", json={
        "citizen_id": "CIT-9999", "service_type": "passport_renewal",
    }).status_code == 422
    assert client.post("/api/v1/service-requests", json={
        "citizen_id": "unknown", "service_type": "tax_clearance",
    }).status_code == 422


@pytest.mark.parametrize(
    "payload",
    [
        {"citizen_id":"CIT-9201","service_type":"tax_clearance","departments":["identity","unknown"]},
        {"citizen_id":"CIT-9201","service_type":"tax_clearance","departments":["identity","identity"]},
        {"citizen_id":"CIT-9201","service_type":"tax_clearance","departments":["identity"],"ttl_hours":0},
        {"citizen_id":"CIT-9201","service_type":"tax_clearance","departments":["identity"],"ttl_hours":721},
    ],
)
def test_invalid_consent_inputs_are_rejected(client, payload):
    assert client.post("/api/v1/consent", json=payload).status_code == 422


def test_repeated_active_consent_is_updated_not_duplicated(client, session_factory):
    payload = {
        "citizen_id": "CIT-9301", "service_type": "tax_clearance",
        "departments": ["identity", "tax"],
    }
    first = client.post("/api/v1/consent", json=payload)
    second = client.post("/api/v1/consent", json={**payload, "ttl_hours": 48})
    assert first.status_code == second.status_code == 201
    assert first.json()["id"] == second.json()["id"]
