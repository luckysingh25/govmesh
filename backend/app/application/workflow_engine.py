"""Workflow orchestration engine.

Manages the lifecycle of workflow instances and their constituent steps,
including creation, execution, retry with exponential backoff, and
status propagation back to the parent ServiceRequest.
"""

import asyncio
import logging
import math
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Type

from sqlalchemy.orm import Session

from app.connectors.base import BaseConnector, ConnectorResult
from app.connectors.identity import IdentityConnector
from app.connectors.municipality import MunicipalityConnector
from app.connectors.property import PropertyConnector
from app.connectors.tax import TaxConnector
from app.core.config import settings
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowStepInstance
from app.application.intelligence_service import IntelligenceService

logger = logging.getLogger(__name__)

# ── Retry configuration ───────────────────────────────────────────────
MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 2
MAX_BACKOFF_SECONDS = 30

# ── Department → Connector mapping ────────────────────────────────────
CONNECTOR_MAP: Dict[str, Type[BaseConnector]] = {
    "identity": IdentityConnector,
    "property": PropertyConnector,
    "municipality": MunicipalityConnector,
    "tax": TaxConnector,
}


class WorkflowEngine:
    """Core orchestration engine for sequential department workflows."""

    # ── Public API ─────────────────────────────────────────────────────

    def start_workflow(
        self,
        db: Session,
        service_request_id: str,
        citizen_id: str,
        definition_name: str = "business_registration",
    ) -> WorkflowInstance:
        """Create a WorkflowInstance (and its steps) from a definition template.

        GovMesh currently supports reliable synchronous execution. The caller
        invokes `execute_workflow_sync` after this method creates the steps.
        """
        if settings.workflow_execution_mode != "sync":
            raise RuntimeError("Only synchronous workflow execution is currently supported")
        defn = (
            db.query(WorkflowDefinition)
            .filter_by(name=definition_name)
            .first()
        )
        if defn is None:
            raise ValueError(f"Unknown workflow definition: {definition_name}")

        instance = WorkflowInstance(
            definition_id=defn.id,
            service_request_id=service_request_id,
            citizen_id=citizen_id,
            status="pending",
            current_step_index=0,
        )
        db.add(instance)
        db.flush()  # populate instance.id

        for idx, step_name in enumerate(defn.steps):
            step = WorkflowStepInstance(
                workflow_instance_id=instance.id,
                step_name=step_name,
                step_index=idx,
                status="pending",
                attempt_count=0,
                max_retries=MAX_RETRIES,
                correlation_id=(db.query(ServiceRequest).filter_by(request_id=service_request_id).first().correlation_id),
            )
            db.add(step)

        db.commit()
        db.refresh(instance)

        logger.info(
            "workflow_created workflow_id=%s request_id=%s steps=%s",
            instance.workflow_id, service_request_id, defn.steps,
        )

        return instance

    async def execute_step(
        self, db: Session, step_instance_id: int, *, allow_retry: bool = True
    ) -> None:
        """Execute a single workflow step (connector call) and handle the result."""
        step = db.get(WorkflowStepInstance, step_instance_id)
        if step is None:
            logger.error("step_not_found id=%s", step_instance_id)
            return

        workflow = db.get(WorkflowInstance, step.workflow_instance_id)
        if workflow is None:
            logger.error("workflow_not_found for step id=%s", step_instance_id)
            return

        # Mark step as running
        step.status = "running"
        step.attempt_count += 1
        step.started_at = datetime.now(timezone.utc)
        step.error_message = None
        if workflow.status == "pending":
            workflow.status = "running"
        db.commit()

        # Run the connector
        connector_cls = CONNECTOR_MAP.get(step.step_name)
        if connector_cls is None:
            step.status = "failed"
            step.error_message = f"No connector for department: {step.step_name}"
            step.completed_at = datetime.now(timezone.utc)
            db.commit()
            self._advance_or_finish(db, workflow)
            return

        connector = self._connector_for_step(db, step)
        started = time.perf_counter()
        try:
            result = await connector.fetch_data(workflow.citizen_id, step.correlation_id)
        except Exception as exc:
            result = ConnectorResult(step.step_name, "failed", {}, str(exc))
        finally:
            await connector.close()
        result.duration_ms = max(0, round((time.perf_counter() - started) * 1000))

        self._handle_step_result(db, step, workflow, result, allow_retry=allow_retry)

    # ── Synchronous fallback (no Redis) ────────────────────────────────

    async def execute_workflow_sync(self, db: Session, workflow_instance_id: int) -> None:
        """Run all steps inline — optimized with concurrent connector execution and batch commit."""
        workflow = db.get(WorkflowInstance, workflow_instance_id)
        if workflow is None:
            return

        workflow.status = "running"
        for s in workflow.steps:
            s.status = "running"
            s.attempt_count += 1
            s.started_at = datetime.now(timezone.utc)
        db.commit()

        # Run connectors concurrently to reduce latency across network
        async def _run_step_connector(step: WorkflowStepInstance):
            connector_cls = CONNECTOR_MAP.get(step.step_name)
            if connector_cls is None:
                return step, ConnectorResult(step.step_name, "failed", {}, f"No connector for department: {step.step_name}")
            c = self._connector_for_step(db, step)
            started = time.perf_counter()
            try:
                result = await c.fetch_data(workflow.citizen_id, step.correlation_id)
                result.duration_ms = max(0, round((time.perf_counter() - started) * 1000))
                return step, result, datetime.now(timezone.utc)
            except Exception as exc:
                result = ConnectorResult(step.step_name, "failed", {}, str(exc))
                result.duration_ms = max(0, round((time.perf_counter() - started) * 1000))
                return step, result, datetime.now(timezone.utc)
            finally:
                await c.close()

        step_tasks = [_run_step_connector(step) for step in workflow.steps]
        step_outcomes = await asyncio.gather(*step_tasks, return_exceptions=True)

        for outcome in step_outcomes:
            if isinstance(outcome, Exception):
                logger.error("step_execution_exception %s", outcome)
                continue
            step, result, completed_at = outcome
            step.completed_at = completed_at
            self._apply_result_to_step(step, result)

        workflow.current_step_index = max(0, len(workflow.steps) - 1)
        self._finalize_workflow(db, workflow, list(workflow.steps))

    async def resume_pending_tax(self, db: Session, workflow: WorkflowInstance) -> WorkflowInstance:
        """Resume only the persisted tax job; successful steps are never repeated."""
        step = next((item for item in workflow.steps if item.step_name == "tax" and item.status in {"pending", "processing"}), None)
        if step is None or not step.external_job_id:
            return workflow
        connector = TaxConnector()
        started = time.perf_counter()
        try:
            result = await connector.resume_job(step.external_job_id, step.correlation_id)
        finally:
            await connector.close()
        result.duration_ms = max(0, round((time.perf_counter() - started) * 1000))
        step.attempt_count += 1
        step.started_at = datetime.now(timezone.utc)
        step.completed_at = datetime.now(timezone.utc)
        self._apply_result_to_step(step, result)
        self._finalize_workflow(db, workflow, list(workflow.steps))
        db.refresh(workflow)
        return workflow

    async def resume_or_retry(self, db: Session, workflow: WorkflowInstance) -> WorkflowInstance:
        """Resume pending async work or retry one failed department without replaying successes."""
        pending_tax = next((item for item in workflow.steps if item.step_name == "tax" and item.status in {"pending", "processing"}), None)
        if pending_tax:
            return await self.resume_pending_tax(db, workflow)
        retryable = next((item for item in workflow.steps if item.status in {"failed", "timeout", "unavailable", "invalid_response", "schema_incompatible"} and item.attempt_count < item.max_retries), None)
        if retryable:
            await self.execute_step(db, retryable.id, allow_retry=False)
            db.refresh(workflow)
        return workflow

    # ── Retry logic ────────────────────────────────────────────────────

    def retry_step(self, db: Session, step_instance_id: int) -> bool:
        """Schedule a step for retry with exponential backoff.

        Returns True if a retry was scheduled, False if retries are exhausted.
        """
        step = db.get(WorkflowStepInstance, step_instance_id)
        if step is None:
            return False

        if step.attempt_count >= step.max_retries:
            logger.info("retries_exhausted step_id=%s attempts=%s", step.id, step.attempt_count)
            return False

        delay = min(
            BASE_BACKOFF_SECONDS * (2 ** step.attempt_count),
            MAX_BACKOFF_SECONDS,
        )
        next_retry = datetime.now(timezone.utc) + timedelta(seconds=delay)

        step.status = "retrying"
        step.next_retry_at = next_retry
        step.completed_at = None
        db.commit()

        logger.info(
            "retry_scheduled step_id=%s attempt=%s delay=%ss next=%s",
            step.id, step.attempt_count + 1, delay, next_retry.isoformat(),
        )

        return True

    # ── Internal helpers ───────────────────────────────────────────────

    def _handle_step_result(
        self,
        db: Session,
        step: WorkflowStepInstance,
        workflow: WorkflowInstance,
        result: ConnectorResult,
        *,
        allow_retry: bool,
    ) -> None:
        """Process the connector result — update step, decide retry or advance."""
        step.completed_at = datetime.now(timezone.utc)

        self._apply_result_to_step(step, result)

        if result.status == "success":
            db.commit()
            self._advance_or_finish(db, workflow)
        else:
            db.commit()

            # Attempt retry
            if not allow_retry or not self.retry_step(db, step.id):
                # Retries exhausted — move on to next step (graceful degradation)
                self._advance_or_finish(db, workflow)

    def _advance_or_finish(self, db: Session, workflow: WorkflowInstance) -> None:
        """Move to the next step or mark workflow as complete."""
        db.refresh(workflow)
        steps = list(workflow.steps)
        total = len(steps)
        next_idx = workflow.current_step_index + 1

        if next_idx < total:
            workflow.current_step_index = next_idx
            db.commit()

        else:
            # All steps processed — compute overall status
            self._finalize_workflow(db, workflow, steps)

    def _finalize_workflow(
        self, db: Session, workflow: WorkflowInstance, steps: list[WorkflowStepInstance]
    ) -> None:
        """Set final workflow status and propagate to the ServiceRequest."""
        successes = sum(1 for s in steps if s.status == "success")
        now = datetime.now(timezone.utc)

        has_pending = any(s.status in {"pending", "processing"} for s in steps)
        if has_pending:
            workflow.status = "pending_external"
        elif successes == len(steps):
            workflow.status = "success"
        elif successes > 0:
            workflow.status = "partially_completed"
        else:
            workflow.status = "failed"

        workflow.completed_at = None if has_pending else now
        db.commit()

        # Update the parent ServiceRequest
        sr = (
            db.query(ServiceRequest)
            .filter_by(request_id=workflow.service_request_id)
            .first()
        )
        if sr:
            sr.status = workflow.status
            sr.completed_at = None if has_pending else now
            db.commit()

        logger.info(
            "workflow_finalized workflow_id=%s status=%s successes=%s/%s",
            workflow.workflow_id, workflow.status, successes, len(steps),
        )

    @staticmethod
    def _apply_result_to_step(step: WorkflowStepInstance, result: ConnectorResult) -> None:
        step.status = result.status
        step.result_data = result.data or None
        step.normalized_output = result.data or None
        step.error_message = result.error
        step.protocol = result.protocol
        raw_inspection_enabled = (
            settings.demo_controls_enabled
            and settings.environment.casefold() in {"development", "demo", "test"}
        )
        step.raw_response = result.raw_response if raw_inspection_enabled else None
        step.source_mapping = result.source_mapping
        step.duration_ms = result.duration_ms
        step.schema_version = result.schema_version
        step.mapping_version = result.mapping_version
        step.external_job_id = result.external_job_id

    @staticmethod
    def _connector_for_step(db: Session, step: WorkflowStepInstance) -> BaseConnector:
        connector_cls = CONNECTOR_MAP[step.step_name]
        if step.step_name == "property" and connector_cls is PropertyConnector:
            mapping, version = IntelligenceService().active_property_mapping(db)
            return PropertyConnector(approved_mapping=mapping, mapping_version=version)
        return connector_cls()
