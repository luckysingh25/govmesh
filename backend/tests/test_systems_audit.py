import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import Base, get_db

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

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_create_and_list_systems():
    # Register and login as admin
    client.post("/api/v1/auth/register", json={"email": "admin2@govmesh.com", "password": "password", "role": "admin"})
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
    list_resp = client.get("/api/v1/systems")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1
    assert list_resp.json()[-1]["name"] == "Federal Tax DB"

def test_service_requests_list():
    resp = client.get("/api/v1/service-requests")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
