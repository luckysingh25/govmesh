from copy import deepcopy

from app.connectors.base import ConnectorResult
from app.intelligence import generate_insights


def healthy_results() -> list[ConnectorResult]:
    return [
        ConnectorResult(
            "identity",
            "success",
            {"full_name": "Rajesh Kumar", "date_of_birth": "1985-06-15", "address": "123 MG Road"},
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
            {"municipal_id": "MUN-1", "resident_name": "Rajesh Kumar"},
        ),
        ConnectorResult("tax", "success", {"tax_status": "CLEARED"}),
    ]


def rule_ids(results: list[ConnectorResult]) -> list[str]:
    return [insight.rule_id for insight in generate_insights(results)]


def test_identity_rule_detects_missing_verification_data():
    results = healthy_results()
    results[0].data.pop("date_of_birth")

    assert "IDENTITY_NOT_VERIFIED" in rule_ids(results)


def test_property_rule_detects_missing_required_information():
    results = healthy_results()
    results[1].data["property_id"] = None

    assert "PROPERTY_INFORMATION_MISSING" in rule_ids(results)


def test_municipality_rule_detects_missing_registration():
    results = healthy_results()
    results[2].data = {}

    assert "MUNICIPALITY_REGISTRATION_MISSING" in rule_ids(results)


def test_municipality_rule_detects_inactive_registration():
    results = healthy_results()
    results[2].data["registration_status"] = "INACTIVE"

    assert "MUNICIPALITY_REGISTRATION_MISSING" in rule_ids(results)


def test_tax_rule_detects_uncleared_status():
    results = healthy_results()
    results[3].data["tax_status"] = "DUE"

    assert "TAX_CLEARANCE_NOT_CONFIRMED" in rule_ids(results)


def test_department_rule_detects_pending_or_unavailable_results():
    results = healthy_results()
    results[1] = ConnectorResult("property", "pending", {})
    results[3] = ConnectorResult("tax", "failed", {}, "Tax service unavailable")

    insight = next(item for item in generate_insights(results) if item.rule_id == "DEPARTMENT_RESULTS_UNAVAILABLE")
    assert insight.severity == "warning"
    assert "property, tax" in insight.message


def test_department_rule_uses_info_when_all_unavailable_results_are_pending():
    results = healthy_results()
    results[1] = ConnectorResult("property", "pending", {})

    insight = next(item for item in generate_insights(results) if item.rule_id == "DEPARTMENT_RESULTS_UNAVAILABLE")
    assert insight.severity == "warning"


def test_department_rule_uses_warning_when_a_result_is_missing_and_another_is_pending():
    results = healthy_results()[:-1]
    results[1] = ConnectorResult("property", "pending", {})

    insight = next(item for item in generate_insights(results) if item.rule_id == "DEPARTMENT_RESULTS_UNAVAILABLE")
    assert insight.severity == "warning"
    assert "property, tax" in insight.message


def test_multiple_findings_are_returned_in_stable_rule_order():
    results = healthy_results()
    results[0].data = {"full_name": "Rajesh Kumar"}
    results[1].data = {"property_id": "PROP-1"}
    results[3].data["tax_status"] = "DUE"

    assert rule_ids(results) == [
        "IDENTITY_NOT_VERIFIED",
        "PROPERTY_INFORMATION_MISSING",
        "TAX_CLEARANCE_NOT_CONFIRMED",
    ]


def test_healthy_aggregate_has_no_insights():
    assert generate_insights(healthy_results()) == []


def test_name_mismatch_ignores_case_and_whitespace_but_detects_real_difference():
    results = healthy_results()
    results[1].data["owner_name"] = "  RAJESH   KUMAR "
    assert "CROSS_SYSTEM_NAME_MISMATCH" not in rule_ids(results)

    results[1].data["owner_name"] = "Meera Kumar"
    assert "CROSS_SYSTEM_NAME_MISMATCH" in rule_ids(results)


def test_address_mismatch_detects_real_difference():
    results = healthy_results()
    results[2].data["address"] = "44 Lake Road"

    assert "CROSS_SYSTEM_ADDRESS_MISMATCH" in rule_ids(results)


def test_pending_tax_has_one_specific_info_advisory():
    results = healthy_results()
    results[3] = ConnectorResult("tax", "pending", {"tax_status": "PENDING"})
    insights = generate_insights(results)

    assert [(item.rule_id, item.severity) for item in insights] == [
        ("TAX_CLEARANCE_NOT_CONFIRMED", "info")
    ]


def test_missing_identity_does_not_create_duplicate_identity_advisory():
    results = healthy_results()[1:]

    assert rule_ids(results) == ["DEPARTMENT_RESULTS_UNAVAILABLE"]


def test_missing_departments_and_optional_data_are_handled_safely():
    results = [ConnectorResult("identity", "success", {})]

    assert rule_ids(results) == ["IDENTITY_NOT_VERIFIED", "DEPARTMENT_RESULTS_UNAVAILABLE"]


def test_output_is_deterministic_and_input_is_not_mutated():
    results = healthy_results()
    results[3].data["tax_status"] = "DUE"
    original = deepcopy(results)

    first = generate_insights(results)
    second = generate_insights(results)

    assert first == second
    assert results == original
