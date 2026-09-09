import importlib.util
import json
from pathlib import Path
import re
import sys

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel


ROOT = Path(__file__).resolve().parents[2]
SERVICES = ROOT / "services"
SEED = SERVICES / "seed"
sys.path.insert(0, str(SERVICES))

from seed_loader import load_seed_records  # noqa: E402


class MinimalRecord(BaseModel):
    citizen_id: str


def load_service(name: str):
    path = SERVICES / f"{name}-service" / "app.py"
    spec = importlib.util.spec_from_file_location(f"seeded_{name}_service", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_all_seed_files_load_and_scenarios_are_complete():
    scenarios = json.loads((SEED / "scenarios.json").read_text(encoding="utf-8"))
    assert [row["citizen_id"] for row in scenarios] == [
        f"CIT-{number}" for number in range(1001, 1009)
    ]
    for filename in ("identity.json", "municipality.json", "property.json", "tax.json"):
        records = json.loads((SEED / filename).read_text(encoding="utf-8"))
        assert records


def test_seed_loading_is_deterministic():
    path = SEED / "identity.json"
    first = load_seed_records(path, MinimalRecord)
    second = load_seed_records(path, MinimalRecord)
    assert first == second
    assert list(first) == list(second)


def test_invalid_and_duplicate_seed_records_fail_clearly(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text('[{"wrong":"field"}]', encoding="utf-8")
    with pytest.raises(RuntimeError, match="Invalid record"):
        load_seed_records(invalid, MinimalRecord)

    duplicate = tmp_path / "duplicate.json"
    duplicate.write_text(
        '[{"citizen_id":"CIT-1001"},{"citizen_id":"CIT-1001"}]',
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="Duplicate citizen_id"):
        load_seed_records(duplicate, MinimalRecord)


def test_seed_data_uses_only_explicitly_fictional_identifiers():
    combined = "\n".join(path.read_text(encoding="utf-8") for path in SEED.glob("*.json"))
    assert not re.search(r"\b\d{12}\b", combined)
    assert not re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", combined)
    assert "@" not in combined
    assert "DEMO-TAX-" in combined


@pytest.mark.parametrize(
    ("service", "path", "headers"),
    [
        ("identity", "/api/identity/CIT-9999", {"Authorization": "Bearer demo"}),
        ("municipality", "/api/municipality/CIT-9999", {"x-api-key": "sim_municipality_key"}),
        ("tax", "/api/tax/CIT-9999", {}),
    ],
)
def test_unknown_citizen_returns_not_found(service, path, headers):
    client = TestClient(load_service(service).app)
    assert client.get(path, headers=headers).status_code == 404


def test_unknown_property_returns_soap_not_found():
    client = TestClient(load_service("property").app)
    response = client.post(
        "/soap/property",
        content="<Envelope><citizenId>CIT-9999</citizenId></Envelope>",
        headers={"Content-Type": "text/xml"},
    )
    assert response.status_code == 404
    assert "Property record not found" in response.text


def test_deliberate_scenario_mismatches_are_the_only_inconsistencies():
    identity = {r["citizen_id"]: r for r in json.loads((SEED / "identity.json").read_text())}
    municipality = {r["citizen_id"]: r for r in json.loads((SEED / "municipality.json").read_text())}
    property_records = {r["citizenId"]: r for r in json.loads((SEED / "property.json").read_text())}

    assert property_records["CIT-1006"]["ownerName"] != identity["CIT-1006"]["full_name"]
    assert municipality["CIT-1007"]["address"] != identity["CIT-1007"]["address"]
    for citizen_id in ("CIT-1001", "CIT-1002", "CIT-1004", "CIT-1007", "CIT-1008"):
        assert property_records[citizen_id]["ownerName"] == identity[citizen_id]["full_name"]

