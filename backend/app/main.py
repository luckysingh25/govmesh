import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine
from app.core.redis import check_redis_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("govmesh.request")

app = FastAPI(
    title="GovMesh API",
    version="0.1.0",
    description="GovMesh SIH26129 Interoperable Government-Service API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def correlation_and_request_logging(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    started = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    logger.info(
        "request_completed method=%s path=%s status=%s duration_ms=%d correlation_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        (time.perf_counter() - started) * 1000,
        correlation_id,
    )
    return response

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "correlation_id": getattr(request.state, "correlation_id", None)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", None)
    logger.error("unhandled_exception correlation_id=%s error=%s", correlation_id, exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "correlation_id": correlation_id}
    )

from app.api.endpoints import service_requests, consent, auth, systems, workflows, audit, lineage, timeline, intelligence
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(systems.router, prefix="/api/v1/systems", tags=["systems"])
app.include_router(service_requests.router, prefix="/api/v1/service-requests", tags=["service-requests"])
app.include_router(consent.router, prefix="/api/v1/consent", tags=["consent"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["workflows"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["audit"])
app.include_router(lineage.router, prefix="/api/v1/lineage", tags=["lineage"])
app.include_router(timeline.router, prefix="/api/v1/timeline", tags=["timeline"])
app.include_router(intelligence.router, prefix="/api/v1/intelligence", tags=["intelligence"])


@app.on_event("startup")
def startup_seed():
    """Seed workflow definitions on application startup."""
    from app.db.session import SessionLocal
    from app.db.seed_workflows import seed_workflow_definitions
    try:
        db = SessionLocal()
        seed_workflow_definitions(db)
    except Exception as exc:
        logger.warning("workflow_seed_failed error=%s", exc)
    finally:
        db.close()

@app.get("/health")
def health():
    import time
    
    # Check Database connection
    db_status = {"status": "disconnected", "response_time_ms": 0}
    t0 = time.perf_counter()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = {
                "status": "connected", 
                "response_time_ms": int((time.perf_counter() - t0) * 1000)
            }
    except Exception:
        db_status = {"status": "unavailable", "response_time_ms": 0}

    # Check Redis connection
    redis_status = {"status": "disconnected", "response_time_ms": 0}
    t0 = time.perf_counter()
    try:
        from app.core.redis import check_redis_connection
        if check_redis_connection():
            redis_status = {
                "status": "connected", 
                "response_time_ms": int((time.perf_counter() - t0) * 1000)
            }
        else:
            redis_status = {"status": "unavailable", "response_time_ms": 0}
    except Exception:
        redis_status = {"status": "unavailable", "response_time_ms": 0}

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "database": db_status,
        "redis": redis_status,
    }
