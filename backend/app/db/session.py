from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

import logging

logger = logging.getLogger(__name__)

# Silence raw SQL queries and connection chatter in the terminal
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Standard SQLAlchemy configuration: DNS and routing are owned by the platform.
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for obtaining DB sessions in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
