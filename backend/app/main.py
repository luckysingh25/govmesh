from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine
from app.core.redis import check_redis_connection

app = FastAPI(
    title="GovMesh API",
    version="0.1.0",
    description="GovMesh SIH26129 Interoperable Government-Service API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    # Check Database connection
    db_status = "disconnected"
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        db_status = "unavailable"

    # Check Redis connection
    redis_status = "connected" if check_redis_connection() else "unavailable"

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": db_status,
        "redis": redis_status,
    }
