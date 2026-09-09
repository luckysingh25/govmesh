import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.session import Base
from app.application.data_lineage_service import DataLineageService
from app.application.audit_service import AuditService

@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

@pytest.fixture(scope="module")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_data_lineage_service(db_session):
    service = DataLineageService()
    record = service.record_lineage(
        db_session,
        correlation_id="corr-123",
        source_system="Identity",
        source_field="full_name",
        destination_system="Response",
        destination_field="citizen.name",
        transformation="exact match",
        service_request_id="req-456"
    )
    assert record.id is not None
    assert record.correlation_id == "corr-123"
    
    records = service.get_lineage_by_correlation(db_session, "corr-123")
    assert len(records) == 1
    assert records[0].source_field == "full_name"

def test_audit_service_retrieval(db_session):
    service = AuditService()
    service.log_event(
        db_session,
        event_type="Test Event",
        actor="System",
        target="Citizen",
        detail="Detail",
        outcome="success",
        correlation_id="corr-789"
    )
    
    logs = service.get_logs_by_correlation(db_session, "corr-789")
    assert len(logs) == 1
    assert logs[0].correlation_id == "corr-789"
    
    recent = service.get_recent_logs(db_session, limit=10)
    assert len(recent) > 0
