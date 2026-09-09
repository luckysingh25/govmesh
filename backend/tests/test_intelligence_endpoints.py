from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.auth import get_password_hash
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app
from app.models.intelligence import SystemSchema
from app.models.user import User


engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def override_db():
    with Session() as db:
        yield db


app.dependency_overrides[get_db] = override_db
client = TestClient(app)


def token_for(role: str, email: str) -> str:
    with Session() as db:
        db.add(User(email=email, hashed_password=get_password_hash("password123"), role=role))
        db.commit()
    response = client.post("/api/v1/auth/login", data={"username": email, "password": "password123"})
    return response.json()["access_token"]


def test_schema_ingestion_requires_privileged_role():
    app.dependency_overrides[get_db] = override_db
    payload = {"system_name": "Secure System", "schema_content": {"properties": {"id": {"type": "string"}}}}
    assert client.post("/api/v1/intelligence/schemas/ingest", json=payload).status_code == 401

    citizen_token = token_for("citizen", "intel-citizen@govmesh.com")
    forbidden = client.post(
        "/api/v1/intelligence/schemas/ingest",
        json=payload,
        headers={"Authorization": f"Bearer {citizen_token}"},
    )
    assert forbidden.status_code == 403

    steward_token = token_for("data_steward", "steward@govmesh.com")
    created = client.post(
        "/api/v1/intelligence/schemas/ingest",
        json=payload,
        headers={"Authorization": f"Bearer {steward_token}"},
    )
    assert created.status_code == 200


def test_demo_trigger_is_idempotent_and_disabled_in_production():
    app.dependency_overrides[get_db] = override_db
    original_environment = settings.environment
    settings.environment = "test"
    try:
        assert client.post("/api/v1/intelligence/demo/trigger").status_code == 200
        assert client.post("/api/v1/intelligence/demo/trigger").status_code == 200
        with Session() as db:
            count = db.query(SystemSchema).filter_by(system_name="Property System").count()
        assert count == 2

        settings.environment = "production"
        assert client.post("/api/v1/intelligence/demo/trigger").status_code == 404
    finally:
        settings.environment = original_environment
