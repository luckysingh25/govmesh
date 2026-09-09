"""Canonical service-type and workflow department definitions."""

from enum import Enum


class ServiceType(str, Enum):
    BUSINESS_REGISTRATION = "business_registration"
    PROPERTY_TRANSFER = "property_transfer"
    TAX_CLEARANCE = "tax_clearance"


KNOWN_DEPARTMENTS = ("identity", "property", "municipality", "tax")

WORKFLOW_DEFINITIONS = {
    ServiceType.BUSINESS_REGISTRATION.value: {
        "description": "Business registration checks all participating departments",
        "steps": ["identity", "property", "municipality", "tax"],
    },
    ServiceType.PROPERTY_TRANSFER.value: {
        "description": "Property transfer verifies identity, ownership, and municipality registration",
        "steps": ["identity", "property", "municipality"],
    },
    ServiceType.TAX_CLEARANCE.value: {
        "description": "Tax clearance verifies identity and current tax status",
        "steps": ["identity", "tax"],
    },
}


def required_departments(service_type: str | ServiceType) -> tuple[str, ...]:
    value = service_type.value if isinstance(service_type, ServiceType) else service_type
    return tuple(WORKFLOW_DEFINITIONS[value]["steps"])

