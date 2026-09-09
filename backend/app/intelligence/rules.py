from collections.abc import Mapping

from app.connectors.base import ConnectorResult
from app.schemas.service_request import IntelligenceInsight


DEPARTMENTS = ("identity", "property", "municipality", "tax")


def identity_not_verified(
    results: Mapping[str, ConnectorResult],
) -> IntelligenceInsight | None:
    identity = results.get("identity")
    if identity is None or identity.status != "success":
        return IntelligenceInsight(
            rule_id="IDENTITY_NOT_VERIFIED",
            severity="warning",
            message="Identity verification is incomplete because a successful identity result is unavailable.",
        )

    missing = [field for field in ("full_name", "date_of_birth") if not identity.data.get(field)]
    if missing:
        return IntelligenceInsight(
            rule_id="IDENTITY_NOT_VERIFIED",
            severity="warning",
            message=f"Identity verification is incomplete because {', '.join(missing)} is missing.",
        )
    return None


def property_information_missing(
    results: Mapping[str, ConnectorResult],
) -> IntelligenceInsight | None:
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


def municipality_registration_missing(
    results: Mapping[str, ConnectorResult],
) -> IntelligenceInsight | None:
    municipality = results.get("municipality")
    if municipality is None or municipality.status != "success":
        return None
    if municipality.data.get("municipal_id"):
        return None
    return IntelligenceInsight(
        rule_id="MUNICIPALITY_REGISTRATION_MISSING",
        severity="warning",
        message="Municipality registration cannot be confirmed because municipal_id is missing.",
    )


def tax_clearance_not_confirmed(
    results: Mapping[str, ConnectorResult],
) -> IntelligenceInsight | None:
    tax = results.get("tax")
    if tax is None or tax.status != "success":
        return None

    tax_status = tax.data.get("tax_status")
    if isinstance(tax_status, str) and tax_status.strip().casefold() == "cleared":
        return None
    displayed_status = repr(tax_status) if tax_status is not None else "missing"
    return IntelligenceInsight(
        rule_id="TAX_CLEARANCE_NOT_CONFIRMED",
        severity="warning",
        message=f"Tax clearance is not confirmed because tax_status is {displayed_status}.",
    )


def department_results_unavailable(
    results: Mapping[str, ConnectorResult],
) -> IntelligenceInsight | None:
    missing = [department for department in DEPARTMENTS if department not in results]
    unavailable = [
        department
        for department in DEPARTMENTS
        if department not in results
        or results[department].status not in {"success", "not_required"}
    ]
    if not unavailable:
        return None

    statuses = {
        results[department].status
        for department in unavailable
        if department in results
    }
    severity = "info" if not missing and statuses == {"pending"} else "warning"
    return IntelligenceInsight(
        rule_id="DEPARTMENT_RESULTS_UNAVAILABLE",
        severity=severity,
        message=f"Department results are not available for: {', '.join(unavailable)}.",
    )
