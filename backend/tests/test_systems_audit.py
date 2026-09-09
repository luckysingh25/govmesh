import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app as fastapi_app
from app.db.session import Base, get_db

# Import models so Base.metadata knows about them
from app.models.system import System
from app.models.service_request import ServiceRequest
from app.models.audit_log import AuditLog
from app.models.workflow import WorkflowDefinition, WorkflowInstance, WorkflowStepInstance
from app.models.data_lineage import DataLineage
from app.models.intelligence import SystemSchema, SchemaField, MappingSuggestion, ImpactAnalysis
from app.models.user import User
from app.core.auth import get_password_hash

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=test_engine)
Base.metadata.create_all(test_engine)

def override_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

fastapi_app.dependency_overrides[get_db] = override_db

# Mock SessionLocal used in main.py startup event
import app.db.session
app.db.session.SessionLocal = TestSession

client = TestClient(fastapi_app)

def test_create_and_list_systems():
    fastapi_app.dependency_overrides[get_db] = override_db
    # Privileged users are provisioned internally, never through public registration.
    with TestSession() as db:
        db.add(User(email="admin2@govmesh.com", hashed_password=get_password_hash("password"), role="admin"))
        db.commit()
    login = client.post("/api/v1/auth/login", data={"username": "admin2@govmesh.com", "password": "password"})
    token = login.json()["access_token"]

    # Create system
    headers = {"Authorization": f"Bearer {token}"}
    sys_payload = {
        "name": "Federal Tax DB",
        "system_type": "Federal",
        "protocol": "gRPC",
        "status": "Online",
        "uptime_percent": 99.9,
        "latency_ms": 45
    }
    create_resp = client.post("/api/v1/systems", headers=headers, json=sys_payload)
    assert create_resp.status_code == 201
    assert create_resp.json()["name"] == "Federal Tax DB"

    # List systems (unprotected endpoint)
    list_resp = client.get("/api/v1/systems", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1
    assert list_resp.json()[-1]["name"] == "Federal Tax DB"

def test_service_requests_list():
    fastapi_app.dependency_overrides[get_db] = override_db
    with TestSession() as db:
        admin = db.query(User).filter_by(email="admin2@govmesh.com").first()
    token = client.post("/api/v1/auth/login", data={"username": admin.email, "password": "password"}).json()["access_token"]
    resp = client.get("/api/v1/service-requests", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
