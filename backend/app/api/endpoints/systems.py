from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.system import System
from app.schemas.system import SystemResponse, SystemCreate
from app.core.auth import require_roles

router = APIRouter()

@router.get("", response_model=List[SystemResponse])
@router.get("/", response_model=List[SystemResponse], include_in_schema=False)
def list_systems(db: Session = Depends(get_db)):
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
