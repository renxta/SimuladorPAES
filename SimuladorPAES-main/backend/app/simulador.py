# app/simulador.py
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.db import get_db
from app import models

router = APIRouter(prefix="/simulador", tags=["simulador"])

# ---------------------------
# Modelo de solicitud
# ---------------------------
class SimularRequest(BaseModel):
    lenguaje: float
    matematicas: float
    matematicas2: Optional[float] = 0      # Ahora opcional
    ciencias: Optional[float] = 0           # Ahora opcional
    historia: Optional[float] = 0           # Ahora opcional
    nem: float
    ranking: float
    universidad: Optional[str] = None
    carrera: Optional[str] = None
    limit: int = 30

# ---------------------------
# Modelo de respuesta
# ---------------------------
class OpcionPostulacion(BaseModel):
    universidad: str
    carrera: str
    puntaje_ponderado: float
    puntaje_corte: float
    margen: float

# ---------------------------
# Endpoint principal
# ---------------------------
@router.post("/", response_model=List[OpcionPostulacion])
def simular(req: SimularRequest, db: Session = Depends(get_db)):
    q = (
        db.query(
            models.Universidad.nombre.label("universidad"),
            models.Carrera.nombre.label("carrera"),
            models.Ponderacion,
            models.PuntajeCorte.puntaje_minimo,
        )
        .join(models.Carrera, models.Carrera.universidad_id == models.Universidad.id)
        .join(models.Ponderacion, models.Ponderacion.carrera_id == models.Carrera.id)
        .join(models.PuntajeCorte, models.PuntajeCorte.carrera_id == models.Carrera.id)
    )

    if req.universidad:
        q = q.filter(models.Universidad.nombre.ilike(f"%{req.universidad}%"))
    if req.carrera:
        q = q.filter(models.Carrera.nombre.ilike(f"%{req.carrera}%"))

    results = q.limit(req.limit).all()
    out = []

    for r in results:
        ponderado = (
            req.lenguaje * float(r.Ponderacion.w_lenguaje)
            + req.matematicas * float(r.Ponderacion.w_matematicas)
            + req.matematicas2 * float(r.Ponderacion.w_matematicas2)
            + max(
                req.ciencias * float(r.Ponderacion.w_ciencias),
                req.historia * float(r.Ponderacion.w_historia),
            )
            + req.nem * float(r.Ponderacion.w_nem)
            + req.ranking * float(r.Ponderacion.w_ranking)
        )

        corte = float(r.puntaje_minimo or 0)
        margen = round(ponderado - corte, 2)

        out.append(
            OpcionPostulacion(
                universidad=r.universidad,
                carrera=r.carrera,
                puntaje_ponderado=round(ponderado, 2),
                puntaje_corte=corte,
                margen=margen,
            )
        )

    out.sort(key=lambda x: x.margen, reverse=True)
    return out
