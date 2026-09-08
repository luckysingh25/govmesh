import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.application.policy_service import PolicyService
from app.connectors.base import ConnectorResult
from app.connectors.identity import IdentityConnector
from app.connectors.municipality import MunicipalityConnector
from app.connectors.property import PropertyConnector
from app.connectors.tax import TaxConnector
from app.models.service_request import ServiceRequest
from app.schemas.service_request import CitizenInfo, DepartmentResponse, ServiceRequestResponse

logger = logging.getLogger(__name__)


def department_response(result: ConnectorResult) -> DepartmentResponse:
    """Convert the shared internal connector shape into the public API shape."""
    return DepartmentResponse(status=result.status, data=result.data or None, error=result.error)


def overall_status(results: list[ConnectorResult]) -> str:
    successes = sum(result.status == "success" for result in results)
    if successes == len(results):
        return "completed"
    if successes:
        return "partially_completed"
    return "failed"


def _denied_department(name: str, reason: str) -> DepartmentResponse:
    return DepartmentResponse(status="denied", data=None, error=reason)


import time
from app.models.data_request import DataRequest

class ServiceRequestService:
    """Persist a request and coordinate the four simulated department adaptors."""

    async def fetch_department_results(self, db: Session, citizen_id: str, request_id: str) -> list[ConnectorResult]:
        connectors = [IdentityConnector(), PropertyConnector(), MunicipalityConnector(), TaxConnector()]
        names = ("identity", "property", "municipality", "tax")
        
        # Pre-create data requests in DB
        data_requests = []
        for name in names:
            dr = DataRequest(service_request_id=request_id, system_name=name, status="pending")
            db.add(dr)
            data_requests.append(dr)
        db.commit()

        start_time = time.perf_counter()
        try:
            outcomes = await asyncio.gather(*(connector.fetch_data(citizen_id) for connector in connectors), return_exceptions=True)
        finally:
            await asyncio.gather(*(connector.close() for connector in connectors))

        end_time = time.perf_counter()
        elapsed_ms = int((end_time - start_time) * 1000)

        normalized: list[ConnectorResult] = []
        for name, outcome, dr in zip(names, outcomes, data_requests):
            dr.latency_ms = elapsed_ms
            dr.completed_at = datetime.now(timezone.utc)
            if isinstance(outcome, Exception):
                logger.error("department_connector_failed department=%s error=%s", name, outcome)
                dr.status = "failed"
                dr.error_message = str(outcome)
                normalized.append(ConnectorResult(name, "failed", {}, "Department service unavailable"))
            else:
                dr.status = outcome.status
                normalized.append(outcome)
                
        db.commit()
        return normalized

    async def create(
        self, *, db: Session, citizen_id: str, service_type: str, correlation_id: str
    ) -> ServiceRequestResponse:
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        record = ServiceRequest(
            request_id=request_id,
            citizen_id=citizen_id,
            service_type=service_type,
            correlation_id=correlation_id,
            status="processing",
        )
        db.add(record)
        db.commit()

        # --- Policy gate ---
        policy = PolicyService().evaluate(db, citizen_id, service_type, correlation_id)
        if policy.decision == "deny":
            record.status = "denied"
            record.completed_at = datetime.now(timezone.utc)
            db.commit()

            denied = _denied_department
            return ServiceRequestResponse(
                request_id=request_id,
                correlation_id=correlation_id,
                citizen=CitizenInfo(citizen_id=citizen_id),
                identity=denied("identity", policy.reason),
                property=denied("property", policy.reason),
                municipality=denied("municipality", policy.reason),
                tax=denied("tax", policy.reason),
                overall_status="denied",
                consent_id=policy.consent_id,
                policy_decision=policy.reason,
            )

        # --- Consent OK — fetch department data ---
        results = await self.fetch_department_results(db, citizen_id, request_id)
        by_department = {result.department: result for result in results}
        identity = by_department["identity"]
        municipality = by_department["municipality"]

        record.status = overall_status(results)
        record.completed_at = datetime.now(timezone.utc)
        db.commit()

        logger.info(
            "service_request_completed",
            extra={"request_id": request_id, "correlation_id": correlation_id, "status": record.status},
        )
        return ServiceRequestResponse(
            request_id=request_id,
            correlation_id=correlation_id,
            citizen=CitizenInfo(
                citizen_id=citizen_id,
                name=identity.data.get("full_name") or municipality.data.get("resident_name") or "Unknown",
                address=identity.data.get("address") or municipality.data.get("address") or "Unknown",
            ),
            identity=department_response(identity),
            property=department_response(by_department["property"]),
            municipality=department_response(municipality),
            tax=department_response(by_department["tax"]),
            overall_status=record.status,
            consent_id=policy.consent_id,
            policy_decision="Consent verified — access allowed",
        )

