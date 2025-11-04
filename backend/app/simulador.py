# app/routes/simulador.py

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db
from app import models

router = APIRouter(prefix="/simulador", tags=["simulador"])

# ---------------------------
# Esquemas (request/response)
# ---------------------------

class SimularRequest(BaseModel):
    ano: Optional[int] = 2024
    lenguaje: Optional[float] = 0
    matematicas: Optional[float] = 0
    matematicas2: Optional[float] = 0
    ciencias: Optional[float] = 0
    historia: Optional[float] = 0
    nem: Optional[float] = 0
    ranking: Optional[float] = 0
    universidad: Optional[str] = None
    carrera: Optional[str] = None
    area: Optional[str] = None  # 👈 Nuevo filtro directo
    limit: Optional[int] = 120


class OpcionPostulacion(BaseModel):
    universidad: str
    carrera: str
    area: Optional[str]  # 👈 Nueva columna incluida
    puntaje_ponderado: float
    puntaje_corte: float
    margen: float
    ano: int


# ----------- HEALTHCHECK -----------
@router.get("/ping")
def ping():
    return {"ok": True, "service": "simulador", "msg": "pong"}


# ----------------- CATÁLOGOS -----------------
@router.get("/universidades")
def listar_universidades(
    q: Optional[str] = Query(None, description="Filtro contiene"),
    db: Session = Depends(get_db),
):
    query = db.query(models.Universidad)
    if q:
        query = query.filter(models.Universidad.nombre.ilike(f"%{q}%"))
    data = query.order_by(models.Universidad.nombre.asc()).all()
    return [{"id": u.id, "nombre": u.nombre} for u in data]


@router.get("/carreras")
def listar_carreras(
    q: Optional[str] = Query(None, description="Filtro por nombre"),
    universidad: Optional[str] = Query(None, description="Filtro por universidad"),
    area: Optional[str] = Query(None, description="Filtro por área"),
    db: Session = Depends(get_db),
):
    qset = (
        db.query(models.Carrera.id, models.Carrera.nombre, models.Carrera.area, models.Universidad.nombre.label("universidad"))
        .join(models.Universidad, models.Universidad.id == models.Carrera.universidad_id)
    )
    if q:
        qset = qset.filter(models.Carrera.nombre.ilike(f"%{q}%"))
    if universidad:
        qset = qset.filter(models.Universidad.nombre.ilike(f"%{universidad}%"))
    if area:
        qset = qset.filter(models.Carrera.area.ilike(f"%{area}%"))
    qset = qset.order_by(models.Universidad.nombre.asc(), models.Carrera.nombre.asc()).limit(120)
    rows = qset.all()
    return [{"id": r.id, "nombre": r.nombre, "universidad": r.universidad, "area": r.area} for r in rows]


# ----------------------------
# SIMULACIÓN DE PUNTAJES PAES
# ----------------------------
@router.post("/", response_model=List[OpcionPostulacion])
@router.post("/simular", response_model=List[OpcionPostulacion])
def simular(req: SimularRequest, db: Session = Depends(get_db)):

    """
    Calcula puntaje ponderado por carrera según ponderaciones.
    Filtra opcionalmente por universidad, carrera o área.
    """

    # Validación básica
    if (req.lenguaje is None or req.matematicas is None or
        (req.lenguaje == 0 and req.matematicas == 0)):
        raise HTTPException(
            status_code=400,
            detail="Debes ingresar al menos puntajes de Lenguaje y Matemáticas."
        )

    filtros = []
    params = {
        "ano": req.ano,
        "w_lenguaje": req.lenguaje,
        "w_mat1": req.matematicas,
        "w_mat2": req.matematicas2,
        "w_ciencias": req.ciencias,
        "w_historia": req.historia,
        "w_nem": req.nem,
        "w_ranking": req.ranking,
        "limit_": 120,
    }

    if req.universidad:
        filtros.append("AND u.nombre ILIKE :f_uni")
        params["f_uni"] = f"%{req.universidad}%"
    if req.carrera:
        filtros.append("AND c.nombre ILIKE :f_car")
        params["f_car"] = f"%{req.carrera}%"
    if req.area:
        filtros.append("AND c.area ILIKE :f_area")
        params["f_area"] = f"%{req.area}%"

    filtros_sql = "\n".join(filtros)

    sql = text(f"""
        SELECT
            u.nombre AS universidad,
            c.nombre AS carrera,
            c.area AS area,
            (
                :w_lenguaje * p.w_lenguaje
              + :w_mat1    * p.w_matematicas
              + :w_mat2    * p.w_matematicas2
              + GREATEST(:w_ciencias * p.w_ciencias, :w_historia * p.w_historia)
              + :w_nem     * p.w_nem
              + :w_ranking * p.w_ranking
            ) AS puntaje_ponderado,
            COALESCE(pc.puntaje_minimo, 0) AS puntaje_corte,
            (
                :w_lenguaje * p.w_lenguaje
              + :w_mat1    * p.w_matematicas
              + :w_mat2    * p.w_matematicas2
              + GREATEST(:w_ciencias * p.w_ciencias, :w_historia * p.w_historia)
              + :w_nem     * p.w_nem
              + :w_ranking * p.w_ranking
            ) - COALESCE(pc.puntaje_minimo, 0) AS margen,
            :ano AS ano
        FROM carreras c
        JOIN universidades u ON u.id = c.universidad_id
        JOIN ponderaciones p ON p.carrera_id = c.id
        LEFT JOIN puntajes_corte pc
               ON pc.carrera_id = c.id
              AND pc.ano = :ano
        WHERE 1=1
        {filtros_sql}
        ORDER BY margen DESC, puntaje_ponderado DESC
        LIMIT :limit_;
    """)

    rows = db.execute(sql, params).mappings().all()

    out: List[OpcionPostulacion] = []
    for r in rows:
        out.append(
            OpcionPostulacion(
                universidad=r["universidad"],
                carrera=r["carrera"],
                area=r["area"],
                puntaje_ponderado=float(round(r["puntaje_ponderado"], 2)),
                puntaje_corte=float(round(r["puntaje_corte"], 2)),
                margen=float(round(r["margen"], 2)),
                ano=r["ano"],
            )
        )
    return out
