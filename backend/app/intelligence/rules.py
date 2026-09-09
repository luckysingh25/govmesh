from collections.abc import Mapping
import re

from app.connectors.base import ConnectorResult
from app.schemas.service_request import IntelligenceInsight


DEPARTMENTS = ("identity", "property", "municipality", "tax")


def _normalized(value: object) -> str:
    """Normalize human-entered values for deterministic cross-system comparison."""
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def identity_not_verified(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    identity = results.get("identity")
    if identity is None or identity.status != "success":
        return None

    missing = [field for field in ("full_name", "date_of_birth") if not identity.data.get(field)]
    verification_status = _normalized(identity.data.get("verification_status"))
    if missing or verification_status not in {"", "verified"}:
        reason = f"{', '.join(missing)} is missing" if missing else "verification_status is not VERIFIED"
        return IntelligenceInsight(
            rule_id="IDENTITY_NOT_VERIFIED",
            severity="warning",
            message=f"Identity verification is incomplete because {reason}.",
        )
    return None


def property_information_missing(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    property_result = results.get("property")
    if property_result is None or property_result.status != "success":
        return None

    required_fields = ("property_id", "owner_name", "address", "property_type")
    missing = [field for field in required_fields if not property_result.data.get(field)]
    if not missing:
        return None
    return IntelligenceInsight(
        rule_id="PROPERTY_INFORMATION_MISSING",
        severity="warning",
        message=f"Property information is incomplete because {', '.join(missing)} is missing.",
    )


def municipality_registration_missing(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    municipality = results.get("municipality")
    if municipality is None or municipality.status != "success":
        return None
    registration_status = _normalized(municipality.data.get("registration_status"))
    if municipality.data.get("municipal_id") and registration_status not in {"inactive", "suspended"}:
        return None
    reason = (
        f"registration_status is {municipality.data.get('registration_status')!r}"
        if registration_status in {"inactive", "suspended"}
        else "municipal_id is missing"
    )
    return IntelligenceInsight(
        rule_id="MUNICIPALITY_REGISTRATION_MISSING",
        severity="warning",
        message=f"Municipality registration cannot be confirmed because {reason}.",
    )


def tax_clearance_not_confirmed(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    tax = results.get("tax")
    if tax is None or tax.status not in {"success", "pending"}:
        return None

    tax_status = tax.data.get("tax_status")
    if _normalized(tax_status) == "cleared":
        return None
    pending = tax.status == "pending" or _normalized(tax_status) == "pending"
    displayed_status = repr(tax_status) if tax_status is not None else "missing"
    return IntelligenceInsight(
        rule_id="TAX_CLEARANCE_NOT_CONFIRMED",
        severity="info" if pending else "warning",
        message=f"Tax clearance is not confirmed because tax_status is {displayed_status}.",
    )


def cross_system_name_mismatch(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    fields = (
        ("identity", "full_name"),
        ("property", "owner_name"),
        ("municipality", "resident_name"),
    )
    values = {
        _normalized(result.data.get(field))
        for department, field in fields
        if (result := results.get(department)) is not None
        and result.status == "success"
        and result.data.get(field)
    }
    if len(values) <= 1:
        return None
    return IntelligenceInsight(
        rule_id="CROSS_SYSTEM_NAME_MISMATCH",
        severity="warning",
        message="Citizen names do not match across the available department records.",
    )


def cross_system_address_mismatch(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    fields = (("identity", "address"), ("property", "address"), ("municipality", "address"))
    values = {
        _normalized(result.data.get(field))
        for department, field in fields
        if (result := results.get(department)) is not None
        and result.status == "success"
        and result.data.get(field)
    }
    if len(values) <= 1:
        return None
    return IntelligenceInsight(
        rule_id="CROSS_SYSTEM_ADDRESS_MISMATCH",
        severity="warning",
        message="Citizen addresses do not match across the available department records.",
    )


def department_results_unavailable(results: Mapping[str, ConnectorResult]) -> IntelligenceInsight | None:
    unavailable = [
        department
        for department in DEPARTMENTS
        if department not in results
        or results[department].status not in {"success", "not_required"}
    ]
    # A pending tax result already has a specific, more helpful advisory.
    unavailable = [
        department
        for department in unavailable
        if not (department == "tax" and results.get(department) and results[department].status == "pending")
    ]
    if not unavailable:
        return None

    return IntelligenceInsight(
        rule_id="DEPARTMENT_RESULTS_UNAVAILABLE",
        severity="warning",
        message=f"Department results are not available for: {', '.join(unavailable)}.",
    )
