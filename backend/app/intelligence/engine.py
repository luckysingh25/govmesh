from collections.abc import Callable, Mapping, Sequence

from app.connectors.base import ConnectorResult
from app.intelligence.rules import (
    department_results_unavailable,
    identity_not_verified,
    municipality_registration_missing,
    property_information_missing,
    tax_clearance_not_confirmed,
)
from app.schemas.service_request import IntelligenceInsight


Rule = Callable[[Mapping[str, ConnectorResult]], IntelligenceInsight | None]

RULES: tuple[Rule, ...] = (
    identity_not_verified,
    property_information_missing,
    municipality_registration_missing,
    tax_clearance_not_confirmed,
    department_results_unavailable,
)


def generate_insights(results: Sequence[ConnectorResult]) -> list[IntelligenceInsight]:
    """Evaluate normalized connector results without changing the input objects."""
    by_department = {result.department: result for result in results}
    return [insight for rule in RULES if (insight := rule(by_department)) is not None]
