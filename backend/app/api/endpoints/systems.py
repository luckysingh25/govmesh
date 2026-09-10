import asyncio
import time
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.system import System
from app.schemas.system import SystemResponse, SystemCreate
from app.core.auth import require_roles, get_current_user
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[SystemResponse])
@router.get("/", response_model=List[SystemResponse], include_in_schema=False)
def list_systems(db: Session = Depends(get_db), _current_user: User = Depends(get_current_user)):
    return db.query(System).all()

@router.post("", response_model=SystemResponse, status_code=201)
@router.post("/", response_model=SystemResponse, status_code=201, include_in_schema=False)
def create_system(
    system_in: SystemCreate, 
    db: Session = Depends(get_db),
    # Only admins can create systems
    _current_user = Depends(require_roles(["admin"]))
):
    system = db.query(System).filter(System.name == system_in.name).first()
    if system:
        raise HTTPException(status_code=400, detail="System with this name already exists")
    
    new_system = System(**system_in.model_dump())
    db.add(new_system)
    db.commit()
    db.refresh(new_system)
    return new_system

@router.get("/monitoring")
async def get_monitoring(_current_user: User = Depends(get_current_user)):
    from app.core.config import settings

    departments = (
        ("identity", "Identity Service", settings.identity_url, "REST"),
        ("property", "Property Service", settings.property_url, "SOAP"),
        ("municipality", "Municipality Service", settings.municipality_url, "REST"),
        ("tax", "Tax Service", settings.tax_url, "REST"),
    )
    async with httpx.AsyncClient(timeout=2.0) as client:
        return await asyncio.gather(
            *(check_department_health(client, *department) for department in departments)
        )


async def check_department_health(
    client: httpx.AsyncClient,
    identifier: str,
    name: str,
    base_url: str,
    protocol: str,
) -> dict:
    """Measure one real health endpoint without inventing historical metrics."""
    started = time.perf_counter()
    status = "Offline"
    try:
        response = await client.get(f"{base_url.rstrip('/')}/health")
        status = "Online" if response.is_success else "Degraded"
        if response.is_success:
            payload = response.json()
            if str(payload.get("status", "")).casefold() not in {"healthy", "ok", "online"}:
                status = "Degraded"
    except (httpx.TimeoutException, httpx.RequestError):
        status = "Offline"
    except (TypeError, ValueError):
        status = "Degraded"

    return {
        "id": identifier,
        "name": name,
        "system_type": "Department",
        "protocol": protocol,
        "status": status,
        "latency_ms": max(0, round((time.perf_counter() - started) * 1000)),
        "uptime_percent": None,
        "error_rate": None,
    }
