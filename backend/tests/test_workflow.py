"""Tests for the Workflow + Reliability layer.

Covers:
  1. test_workflow_success          — all 4 connectors succeed
  2. test_workflow_department_failure — one connector fails, workflow partially_completed
  3. test_workflow_retry            — connector fails then succeeds on retry
  4. test_workflow_completed        — end-to-end: create service request → workflow → done
"""

import asyncio
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch, MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base
from app.models.service_request import ServiceRequest
from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowStepInstance
from app.connectors.base import ConnectorResult
from app.application.workflow_engine import WorkflowEngine

# ── Shared test fixtures ──────────────────────────────────────────────

TEST_DB_URL = "sqlite:///./test_workflow.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    """Provide a fresh DB session."""
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_definition(db):
    """Seed a business_registration workflow definition."""
    defn = WorkflowDefinition(
        name="business_registration",
        description="Test workflow",
        steps=["identity", "property", "municipality", "tax"],
    )
    db.add(defn)
    db.commit()
    return defn


@pytest.fixture
def seed_service_request(db):
    """Create a ServiceRequest row for testing."""
    sr = ServiceRequest(
        request_id="REQ-TEST0001",
        citizen_id="CIT-1001",
        service_type="business_registration",
        correlation_id="test-corr-001",
        status="processing",
    )
    db.add(sr)
    db.commit()
    return sr


def _success_result(dept: str) -> ConnectorResult:
    return ConnectorResult(dept, "success", {"test": f"{dept}_data"})


def _failed_result(dept: str) -> ConnectorResult:
    return ConnectorResult(dept, "failed", {}, f"{dept} service unavailable")


# ── Test 1: All connectors succeed ────────────────────────────────────

@pytest.mark.asyncio
async def test_workflow_success(db, seed_definition, seed_service_request):
    """When all 4 department connectors succeed, the workflow should be 'success'."""
    engine_instance = WorkflowEngine()

    # Start the workflow
    wf = engine_instance.start_workflow(db, "REQ-TEST0001", "CIT-1001")

    assert wf.status == "pending"
    assert len(wf.steps) == 4
    assert [s.step_name for s in wf.steps] == ["identity", "property", "municipality", "tax"]

    # Mock all connectors to succeed
    mock_connectors = {
        "identity": AsyncMock(return_value=_success_result("identity")),
        "property": AsyncMock(return_value=_success_result("property")),
        "municipality": AsyncMock(return_value=_success_result("municipality")),
        "tax": AsyncMock(return_value=_success_result("tax")),
    }

    with patch.dict(
        "app.application.workflow_engine.CONNECTOR_MAP",
        {
            dept: MagicMock(return_value=MagicMock(
                fetch_data=mock_connectors[dept],
                close=AsyncMock(),
            ))
            for dept in mock_connectors
        },
    ):
        await engine_instance.execute_workflow_sync(db, wf.id)

    db.refresh(wf)
    assert wf.status == "success"
    assert wf.completed_at is not None

    # All steps should be success
    for step in wf.steps:
        db.refresh(step)
        assert step.status == "success"
        assert step.result_data is not None

    # ServiceRequest should be updated
    sr = db.query(ServiceRequest).filter_by(request_id="REQ-TEST0001").first()
    assert sr.status == "success"


# ── Test 2: One connector fails ───────────────────────────────────────

@pytest.mark.asyncio
async def test_workflow_department_failure(db, seed_definition, seed_service_request):
    """When one department fails (retries exhausted), the workflow should be 'partially_completed'."""
    engine_instance = WorkflowEngine()
    wf = engine_instance.start_workflow(db, "REQ-TEST0001", "CIT-1001")

    # Set max_retries=0 for property step to skip retries
    property_step = next(s for s in wf.steps if s.step_name == "property")
    property_step.max_retries = 0
    db.commit()

    mock_connectors = {
        "identity": AsyncMock(return_value=_success_result("identity")),
        "property": AsyncMock(return_value=_failed_result("property")),
        "municipality": AsyncMock(return_value=_success_result("municipality")),
        "tax": AsyncMock(return_value=_success_result("tax")),
    }

    with patch.dict(
        "app.application.workflow_engine.CONNECTOR_MAP",
        {
            dept: MagicMock(return_value=MagicMock(
                fetch_data=mock_connectors[dept],
                close=AsyncMock(),
            ))
            for dept in mock_connectors
        },
    ):
        await engine_instance.execute_workflow_sync(db, wf.id)

    db.refresh(wf)
    assert wf.status == "partially_completed"

    # Property should be failed, others success
    for step in wf.steps:
        db.refresh(step)
        if step.step_name == "property":
            assert step.status == "failed"
            assert step.error_message is not None
        else:
            assert step.status == "success"

    # ServiceRequest is preserved and status updated
    sr = db.query(ServiceRequest).filter_by(request_id="REQ-TEST0001").first()
    assert sr.status == "partially_completed"
    assert sr.completed_at is not None


# ── Test 3: Retry behaviour ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_workflow_retry(db, seed_definition, seed_service_request):
    """A step that fails should be retried and eventually succeed."""
    engine_instance = WorkflowEngine()
    wf = engine_instance.start_workflow(db, "REQ-TEST0001", "CIT-1001")

    # Manually test retry logic on a single step
    identity_step = next(s for s in wf.steps if s.step_name == "identity")

    # First execution: fail
    fail_connector = MagicMock(return_value=MagicMock(
        fetch_data=AsyncMock(return_value=_failed_result("identity")),
        close=AsyncMock(),
    ))

    with patch.dict("app.application.workflow_engine.CONNECTOR_MAP", {"identity": fail_connector}):
        wf.status = "running"
        db.commit()
        await engine_instance.execute_step(db, identity_step.id)

    db.refresh(identity_step)
    assert identity_step.status == "retrying"
    assert identity_step.attempt_count == 1

    # Second execution: succeed
    success_connector = MagicMock(return_value=MagicMock(
        fetch_data=AsyncMock(return_value=_success_result("identity")),
        close=AsyncMock(),
    ))

    with patch.dict("app.application.workflow_engine.CONNECTOR_MAP", {"identity": success_connector}):
        await engine_instance.execute_step(db, identity_step.id)

    db.refresh(identity_step)
    assert identity_step.status == "success"
    assert identity_step.attempt_count == 2
    assert identity_step.result_data is not None


# ── Test 4: End-to-end workflow completion ────────────────────────────

@pytest.mark.asyncio
async def test_workflow_completed(db, seed_definition, seed_service_request):
    """Full lifecycle: start workflow → all steps succeed → SR status updated."""
    engine_instance = WorkflowEngine()
    wf = engine_instance.start_workflow(db, "REQ-TEST0001", "CIT-1001")

    mock_connectors = {
        "identity": AsyncMock(return_value=_success_result("identity")),
        "property": AsyncMock(return_value=_success_result("property")),
        "municipality": AsyncMock(return_value=_success_result("municipality")),
        "tax": AsyncMock(return_value=_success_result("tax")),
    }

    with patch.dict(
        "app.application.workflow_engine.CONNECTOR_MAP",
        {
            dept: MagicMock(return_value=MagicMock(
                fetch_data=mock_connectors[dept],
                close=AsyncMock(),
            ))
            for dept in mock_connectors
        },
    ):
        await engine_instance.execute_workflow_sync(db, wf.id)

    # Verify final workflow state
    db.refresh(wf)
    assert wf.status == "success"
    assert wf.completed_at is not None
    assert wf.current_step_index == 3  # last step index (0-based)

    # Verify all steps completed
    for step in wf.steps:
        db.refresh(step)
        assert step.status == "success"
        assert step.started_at is not None
        assert step.completed_at is not None
        assert step.attempt_count == 1

    # Verify service request updated
    sr = db.query(ServiceRequest).filter_by(request_id="REQ-TEST0001").first()
    assert sr.status == "success"
    assert sr.completed_at is not None
