"""Seed default demonstration users for GovMesh evaluation."""

import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.core.auth import get_password_hash

logger = logging.getLogger(__name__)

DEFAULT_PASSWORD = "GovMesh@2026!"

# Authentic users matching SIH 2026 test fixtures
SEED_USERS = (
    ("admin@govmesh.example", "admin", None),
    ("steward@govmesh.example", "data_steward", None),
    ("citizen1001@govmesh.example", "citizen", "CIT-1001"),
    ("citizen1006@govmesh.example", "citizen", "CIT-1006"),
)


def seed_demo_users(db: Session) -> None:
    """Ensure authentic demo users exist in the database with verified credentials."""
    needs_commit = False
    hashed_pwd = get_password_hash(DEFAULT_PASSWORD)

    for email, role, citizen_id in SEED_USERS:
        user = db.query(User).filter_by(email=email).first()
        if user is None:
            db.add(
                User(
                    email=email,
                    hashed_password=hashed_pwd,
                    role=role,
                    citizen_id=citizen_id,
                )
            )
            needs_commit = True
            logger.info("seeded_demo_user email=%s role=%s", email, role)
        else:
            # Ensure correct role and password in demonstration / development
            updated = False
            if user.role != role:
                user.role = role
                updated = True
            if citizen_id and user.citizen_id != citizen_id:
                user.citizen_id = citizen_id
                updated = True
            if user.hashed_password != hashed_pwd:
                user.hashed_password = hashed_pwd
                updated = True
            if updated:
                needs_commit = True

    if needs_commit:
        db.commit()
