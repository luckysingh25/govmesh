from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

import json
import logging
import socket
import urllib.request
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def _get_connect_args(db_url: str) -> dict:
    """Resolve database hostname with DNS-over-HTTPS fallback if local DNS fails."""
    try:
        parsed = urlparse(db_url)
        hostname = parsed.hostname
        if not hostname or hostname in ("localhost", "127.0.0.1"):
            return {}
        try:
            socket.gethostbyname(hostname)
            return {}
        except socket.gaierror:
            logger.warning(f"Local DNS failed for {hostname}, trying DNS-over-HTTPS fallback...")
            req = urllib.request.Request(
                f"https://dns.google/resolve?name={hostname}&type=A",
                headers={"User-Agent": "GovMesh-DNS"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                for ans in data.get("Answer", []):
                    if ans.get("type") == 1:
                        logger.info(f"Resolved {hostname} -> {ans['data']} via DNS-over-HTTPS")
                        return {"hostaddr": ans["data"]}
    except Exception as exc:
        logger.warning(f"DNS fallback resolution error: {exc}")
    
    # Fallback to known IP if domain is Neon us-east-2
    if "ep-floral-bird" in db_url:
        return {"hostaddr": "18.226.144.228"}
    return {}

_connect_args = _get_connect_args(settings.database_url)

# Silence raw SQL queries and connection chatter in the terminal
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Create engine with Neon-optimized pool tuning and connect_args
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=False,
    connect_args=_connect_args,
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
