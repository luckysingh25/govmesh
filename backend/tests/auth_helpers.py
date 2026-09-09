from uuid import uuid4

from app.core.auth import create_access_token, get_password_hash
from app.models.user import User


def admin_headers(session_factory) -> dict[str, str]:
    email = f"test-admin-{uuid4().hex}@govmesh.example"
    with session_factory() as db:
        db.add(User(email=email, hashed_password=get_password_hash("test-password-only"), role="admin"))
        db.commit()
    token = create_access_token({"sub": email, "role": "admin"})
    return {"Authorization": f"Bearer {token}"}


def citizen_headers(session_factory, citizen_id: str) -> dict[str, str]:
    email = f"{citizen_id.lower()}-{uuid4().hex}@govmesh.example"
    with session_factory() as db:
        db.add(User(email=email, hashed_password=get_password_hash("test-password-only"), role="citizen", citizen_id=citizen_id))
        db.commit()
    token = create_access_token({"sub": email, "role": "citizen"})
    return {"Authorization": f"Bearer {token}"}
