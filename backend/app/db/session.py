# GovMesh SQLAlchemy Session Engine

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


logger = logging.getLogger(__name__)

# Silence raw SQL queries and connection chatter in the terminal.
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

elif (
    settings.database_url.startswith("postgresql")
    or settings.database_url.startswith("postgres")
):
    connect_args["connect_timeout"] = 5


# Standard SQLAlchemy configuration:
# DNS and routing are owned by the platform.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    """Dependency for obtaining DB sessions in FastAPI routes."""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()