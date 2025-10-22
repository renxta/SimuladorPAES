# app/routes/carreras.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.models import Carrera
from app.schemas import CarreraOut

router = APIRouter(prefix="/carreras", tags=["carreras"])

@router.get("/", response_model=List[CarreraOut])
def listar_carreras(
    universidad_id: Optional[int] = Query(None, description="Filtra por universidad_id"),
    db: Session = Depends(get_db),
):
    q = db.query(Carrera)
    if universidad_id is not None:
        q = q.filter(Carrera.universidad_id == universidad_id)
    return q.order_by(Carrera.nombre).all()

@router.get("/{carrera_id}", response_model=CarreraOut)
def obtener_carrera(carrera_id: int, db: Session = Depends(get_db)):
    return db.query(Carrera).get(carrera_id)
