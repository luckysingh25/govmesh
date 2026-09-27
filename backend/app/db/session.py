# GovMesh SQLAlchemy Session Engine

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


logger = logging.getLogger(__name__)

# Silence raw SQL queries and connection chatter in the terminal.
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


connect_args = {}
db_url = settings.database_url

if db_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False
    engine = create_engine(
        db_url,
        echo=False,
        connect_args=connect_args,
    )
else:
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    connect_args["connect_timeout"] = 10
    
    # High-performance persistent connection pooling for Cloud PostgreSQL (Neon)
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=15,
        pool_recycle=1800,
        pool_pre_ping=False,  # Skip extra network ping roundtrips on every request
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