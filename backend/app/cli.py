"""Development-only administration commands.

Usage: python -m app.cli create-demo-users --password-from-env GOVMESH_DEMO_PASSWORD
"""

import argparse
import os

from app.core.auth import get_password_hash
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.user import User


DEMO_USERS = (
    ("citizen1001@govmesh.example", "citizen", "CIT-1001"),
    ("citizen1002@govmesh.example", "citizen", "CIT-1002"),
    ("citizen1006@govmesh.example", "citizen", "CIT-1006"),
    ("citizen1008@govmesh.example", "citizen", "CIT-1008"),
    ("steward@govmesh.example", "data_steward", None),
    ("admin@govmesh.example", "admin", None),
)


def create_demo_users(password_env: str) -> None:
    if settings.environment.casefold() not in {"development", "demo"}:
        raise SystemExit("Demo users can only be created in development or demo environments")
    password = os.environ.get(password_env)
    if not password or len(password) < 12:
        raise SystemExit(f"Set {password_env} to a password of at least 12 characters")
    with SessionLocal() as db:
        for email, role, citizen_id in DEMO_USERS:
            user = db.query(User).filter_by(email=email).first()
            if user is None:
                db.add(User(email=email, hashed_password=get_password_hash(password), role=role, citizen_id=citizen_id))
            else:
                user.hashed_password = get_password_hash(password)
                user.role = role
                user.citizen_id = citizen_id
        db.commit()
    print(f"Created or updated {len(DEMO_USERS)} fictional demo accounts; password was not logged")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    create = sub.add_parser("create-demo-users")
    create.add_argument("--password-from-env", default="GOVMESH_DEMO_PASSWORD")
    args = parser.parse_args()
    if args.command == "create-demo-users":
        create_demo_users(args.password_from_env)


if __name__ == "__main__":
    main()
