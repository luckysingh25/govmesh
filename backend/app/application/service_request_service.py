import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.application.policy_service import PolicyService
from app.application.workflow_engine import WorkflowEngine
from app.connectors.base import ConnectorResult
from app.connectors.identity import IdentityConnector
from app.connectors.municipality import MunicipalityConnector
from app.connectors.property import PropertyConnector
from app.connectors.tax import TaxConnector
from app.core.config import settings
from app.core.service_types import KNOWN_DEPARTMENTS
from app.intelligence import generate_insights
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowInstance
from app.schemas.service_request import CitizenInfo, DepartmentResponse, ServiceRequestResponse
from app.application.data_lineage_service import DataLineageService
from app.application.audit_service import AuditService

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

    def __init__(self):
        self._workflow_engine = WorkflowEngine()
        self._data_lineage = DataLineageService()
        self._audit = AuditService()

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

        self._audit.log_event(
            db=db,
            event_type="Service Request Started",
            actor=f"Citizen ({citizen_id})",
            target="GovMesh Core",
            detail=f"Initiated {service_type}",
            outcome="success",
            correlation_id=correlation_id
        )

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

        # --- Consent OK — start the workflow ---
        workflow_instance = self._workflow_engine.start_workflow(
            db=db,
            service_request_id=request_id,
            citizen_id=citizen_id,
            definition_name=service_type,
        )
        workflow_id = workflow_instance.workflow_id

        # Synchronous execution is the explicit, reliable prototype default.
        if settings.workflow_execution_mode != "sync":
            raise RuntimeError("Unsupported workflow execution mode")
        await self._workflow_engine.execute_workflow_sync(db, workflow_instance.id)
        db.refresh(workflow_instance)

        # Build response from workflow step results
        db.refresh(record)
        dept_results = self._build_dept_responses(workflow_instance)
        insight_results = []
        for department in KNOWN_DEPARTMENTS:
            response = self._step_to_dept(department, workflow_instance)
            insight_results.append(ConnectorResult(
                department,
                response.status,
                response.data or {},
                response.error,
            ))
        insights = generate_insights(insight_results)

        logger.info(
            "service_request_completed",
            extra={"request_id": request_id, "correlation_id": correlation_id, "status": record.status},
        )

        # Record data lineage for name and address mappings
        citizen_name = "Unknown"
        citizen_address = "Unknown"

        identity_data = dept_results.get("identity", {})
        municipality_data = dept_results.get("municipality", {})

        if identity_data.get("full_name"):
            citizen_name = identity_data["full_name"]
            self._data_lineage.record_lineage(db, correlation_id, "Identity DB", "full_name", "GovMesh Response", "citizen.name", "exact match", request_id)
        elif municipality_data.get("resident_name"):
            citizen_name = municipality_data["resident_name"]
            self._data_lineage.record_lineage(db, correlation_id, "Municipality Records", "resident_name", "GovMesh Response", "citizen.name", "fallback map", request_id)

        if identity_data.get("address"):
            citizen_address = identity_data["address"]
            self._data_lineage.record_lineage(db, correlation_id, "Identity DB", "address", "GovMesh Response", "citizen.address", "exact match", request_id)
        elif municipality_data.get("address"):
            citizen_address = municipality_data["address"]
            self._data_lineage.record_lineage(db, correlation_id, "Municipality Records", "address", "GovMesh Response", "citizen.address", "fallback map", request_id)

        self._audit.log_event(
            db=db,
            event_type="Service Request Completed",
            actor="GovMesh Workflow Engine",
            target=f"Citizen ({citizen_id})",
            detail=f"Status: {record.status}",
            outcome="success" if record.status == "completed" else "warning",
            correlation_id=correlation_id
        )

        return ServiceRequestResponse(
            request_id=request_id,
            correlation_id=correlation_id,
            citizen=CitizenInfo(
                citizen_id=citizen_id,
                name=citizen_name,
                address=citizen_address,
            ),
            identity=self._step_to_dept("identity", workflow_instance),
            property=self._step_to_dept("property", workflow_instance),
            municipality=self._step_to_dept("municipality", workflow_instance),
            tax=self._step_to_dept("tax", workflow_instance),
            overall_status=record.status,
            consent_id=policy.consent_id,
            policy_decision="Consent verified — access allowed",
            insights=insights,
            workflow_id=workflow_id,
        )

    # ── Helpers ─────────────────────────────────────────────────────

    def _build_dept_responses(self, workflow: WorkflowInstance) -> dict:
        """Extract result_data keyed by step_name from workflow steps."""
        data = {}
        for step in workflow.steps:
            data[step.step_name] = step.result_data or {}
        return data

    def _step_to_dept(self, dept_name: str, workflow: WorkflowInstance) -> DepartmentResponse:
        """Convert a workflow step into a DepartmentResponse."""
        for step in workflow.steps:
            if step.step_name == dept_name:
                return DepartmentResponse(
                    status=step.status,
                    data=step.result_data if step.result_data else None,
                    error=step.error_message,
                )
        return DepartmentResponse(status="not_required", data=None, error=None)
