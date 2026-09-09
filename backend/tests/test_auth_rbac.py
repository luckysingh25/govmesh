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

def test_register_and_login():
    app.dependency_overrides[get_db] = override_db
    # Register
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@govmesh.com", "password": "securepassword", "role": "citizen"}
    )
    assert reg_response.status_code == 201
    assert reg_response.json()["email"] == "test@govmesh.com"
    assert reg_response.json()["role"] == "citizen"

    # Login
    login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "test@govmesh.com", "password": "securepassword"}
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token is not None

    # Get Me
    me_response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "test@govmesh.com"

def test_rbac_protection():
    app.dependency_overrides[get_db] = override_db
    # Register citizen
    client.post(
        "/api/v1/auth/register",
        json={"email": "citizen@govmesh.com", "password": "securepassword", "role": "citizen"}
    )
    # Login citizen
    login_resp = client.post(
        "/api/v1/auth/login",
        data={"username": "citizen@govmesh.com", "password": "securepassword"}
    )
    token = login_resp.json()["access_token"]

    # Try to access protected system endpoint
    sys_resp = client.post(
        "/api/v1/systems",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "New System", "system_type": "Test", "protocol": "REST"}
    )
    # Should be forbidden since role is citizen
    assert sys_resp.status_code == 403


def test_public_registration_rejects_role_elevation_and_weak_passwords():
    app.dependency_overrides[get_db] = override_db
    elevated = client.post(
        "/api/v1/auth/register",
        json={"email": "attacker@govmesh.com", "password": "securepassword", "role": "admin"},
    )
    weak = client.post(
        "/api/v1/auth/register",
        json={"email": "weak@govmesh.com", "password": "short", "role": "citizen"},
    )

    assert elevated.status_code == 422
    assert weak.status_code == 422
