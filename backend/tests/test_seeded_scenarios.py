import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.connectors.base import ConnectorResult
from app.db.seed_workflows import seed_workflow_definitions
from app.db.session import Base, get_db
from app.main import app
from tests.auth_helpers import admin_headers


SEED_DIR = Path(__file__).resolve().parents[2] / "services" / "seed"


def load_seed(name):
    return json.loads((SEED_DIR / name).read_text(encoding="utf-8"))


RECORDS = {
    "identity": {row["citizen_id"]: row for row in load_seed("identity.json")},
    "property": {row["citizenId"]: row for row in load_seed("property.json")},
    "municipality": {row["citizen_id"]: row for row in load_seed("municipality.json")},
    "tax": {row["citizenId"]: row for row in load_seed("tax.json")},
}
SCENARIOS = {row["citizen_id"]: row for row in load_seed("scenarios.json")}


def normalized_result(department, citizen_id):
    row = RECORDS[department].get(citizen_id)
    if row is None:
        return ConnectorResult(department, "not_found", {}, f"{department.capitalize()} record was not found")
    if department == "identity":
        data = {key: row[key] for key in ("full_name", "date_of_birth", "address", "verification_status")}
    elif department == "property":
        data = {
            "property_id": row["propertyId"], "owner_name": row["ownerName"],
            "address": row["propertyAddress"], "property_type": row["propertyType"],
            "ownership_status": row["ownershipStatus"],
        }
    elif department == "municipality":
        data = {key: row[key] for key in ("municipal_id", "resident_name", "ward", "address", "registration_status")}
    else:
        data = {
            "tax_id": row["taxId"], "taxpayer_name": row["taxpayerName"],
            "tax_status": row["taxStatus"], "outstanding_amount": row["outstandingAmount"],
            "assessment_year": row["assessmentYear"],
        }
        if row["taxStatus"] == "PENDING":
            return ConnectorResult("tax", "pending", data)
    return ConnectorResult(department, "success", data)


class SeedConnector:
    department = ""

    async def fetch_data(self, citizen_id, correlation_id=None):
        return normalized_result(self.department, citizen_id)

    async def close(self):
        return None


def connector_class(department):
    return type(f"{department.title()}SeedConnector", (SeedConnector,), {"department": department})


@pytest.fixture
def client(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    with Session() as db:
        seed_workflow_definitions(db)

    def override_db():
        with Session() as db:
            yield db

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(
        "app.application.workflow_engine.CONNECTOR_MAP",
        {department: connector_class(department) for department in RECORDS},
    )
    yield TestClient(app, headers=admin_headers(Session))
    app.dependency_overrides.clear()
    engine.dispose()


@pytest.mark.parametrize("citizen_id", ["CIT-1001", "CIT-1002", "CIT-1003", "CIT-1006", "CIT-1008"])
def test_seeded_business_registration_scenarios(client, citizen_id):
    scenario = SCENARIOS[citizen_id]
    consent = client.post("/api/v1/consent", json={
        "citizen_id": citizen_id,
        "service_type": "business_registration",
        "departments": ["identity", "property", "municipality", "tax"],
    })
    assert consent.status_code == 201

    response = client.post("/api/v1/service-requests", json={
        "citizen_id": citizen_id,
        "service_type": "business_registration",
    })
    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] == scenario["expected_overall_status"]
    assert [item["rule_id"] for item in payload["insights"]] == scenario["expected_insight_rule_ids"]

    for department, expected_status in scenario["department_states"].items():
        assert payload[department]["status"] == expected_status
