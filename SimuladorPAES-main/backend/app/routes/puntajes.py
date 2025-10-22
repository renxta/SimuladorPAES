# app/routes/puntajes.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ..db import get_db
from .. import models

router = APIRouter(prefix="/puntajes", tags=["puntajes"])

@router.get("/buscar")
def buscar_puntajes(
    universidad: str = Query(..., description="Nombre (o parte) de la universidad"),
    carrera: str = Query(..., description="Nombre (o parte) de la carrera"),
    ano: int = Query(..., description="Año del puntaje de corte"),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(
            models.Universidad.nombre.label("universidad"),
            models.Carrera.nombre.label("carrera"),
            models.PuntajeCorte.ano,
            models.PuntajeCorte.puntaje_minimo.label("puntaje"),
        )
        .join(models.Carrera, models.Carrera.universidad_id == models.Universidad.id)
        .join(models.PuntajeCorte, models.PuntajeCorte.carrera_id == models.Carrera.id)
        .filter(models.Universidad.nombre.ilike(f"%{universidad}%"))
        .filter(models.Carrera.nombre.ilike(f"%{carrera}%"))
        .filter(models.PuntajeCorte.ano == ano)
        .order_by(models.Carrera.nombre)
        .all()
    )

    # Convertir Row -> dict
    return [dict(r._mapping) for r in rows]
