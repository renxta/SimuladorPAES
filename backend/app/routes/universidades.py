# app/routes/universidades.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import Universidad
from app.schemas import UniversidadOut

router = APIRouter(prefix="/universidades", tags=["universidades"])

@router.get("/", response_model=List[UniversidadOut])
def listar_universidades(db: Session = Depends(get_db)):
    return db.query(Universidad).order_by(Universidad.nombre).all()

@router.get("/{universidad_id}", response_model=UniversidadOut)
def obtener_universidad(universidad_id: int, db: Session = Depends(get_db)):
    return db.query(Universidad).get(universidad_id)
