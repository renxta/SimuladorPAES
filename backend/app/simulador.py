# app/routes/simulador.py
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db import get_db  # tu SessionLocal y dependencia
#
from app import models

router = APIRouter(prefix="/simulador", tags=["simulador"])

# ---------------------------
# Esquemas (request/response)
# ---------------------------

class SimularRequest(BaseModel):
    ano: int = Field(..., description="Año de referencia para comparar puntaje de corte")
    lenguaje: float = 0
    matematicas: float = 0
    matematicas2: float = 0
    ciencias: float = 0
    historia: float = 0
    nem: float = 0
    ranking: float = 0
    universidad: Optional[str] = Field(None, description="Filtro contiene (case-insensitive)")
    carrera: Optional[str] = Field(None, description="Filtro contiene (case-insensitive)")
    limit: int = 30

class OpcionPostulacion(BaseModel):
    universidad: str
    carrera: str
    puntaje_ponderado: float
    puntaje_corte: float
    margen: float
    ano: int

# -----------
# Healthcheck
# -----------
@router.get("/ping")
def ping():
    return {"ok": True, "service": "simulador", "msg": "pong"}


# -----------------
# Catálogos simples
# -----------------
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
    q: Optional[str] = Query(None, description="Filtro contiene sobre nombre de carrera"),
    universidad: Optional[str] = Query(None, description="Filtro contiene sobre nombre de universidad"),
    db: Session = Depends(get_db),
):
    qset = (
        db.query(models.Carrera.id, models.Carrera.nombre, models.Universidad.nombre.label("universidad"))
        .join(models.Universidad, models.Universidad.id == models.Carrera.universidad_id)
    )
    if q:
        qset = qset.filter(models.Carrera.nombre.ilike(f"%{q}%"))
    if universidad:
        qset = qset.filter(models.Universidad.nombre.ilike(f"%{universidad}%"))
    qset = qset.order_by(models.Universidad.nombre.asc(), models.Carrera.nombre.asc()).limit(200)
    rows = qset.all()
    return [{"id": r.id, "nombre": r.nombre, "universidad": r.universidad} for r in rows]


# ----------------------------
# Simulación de puntajes PAES
# ----------------------------
@router.post("/", response_model=List[OpcionPostulacion])
@router.post("/simular", response_model=List[OpcionPostulacion])
def simular(req: SimularRequest, db: Session = Depends(get_db)):
    """
    Calcula puntaje ponderado por carrera según tabla ponderaciones.
    Compara contra puntajes_corte del año req.ano (si existe).
    Usa la mejor entre Ciencias e Historia (la que rinde mejor con su respectivo peso).

    Filtros opcionales:
      - universidad: contiene (case-insensitive)
      - carrera: contiene (case-insensitive)
    """

    # Construimos filtros dinámicos
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
        "limit_": max(1, min(req.limit, 100)),
    }

    if req.universidad:
        filtros.append("AND u.nombre LIKE :f_uni")
        params["f_uni"] = f"%{req.universidad}%"
    if req.carrera:
        filtros.append("AND c.nombre LIKE :f_car")
        params["f_car"] = f"%{req.carrera}%"

    filtros_sql = "\n".join(filtros)

    # SQL (MySQL-compatible) usando ponderaciones y el mejor de ciencias/historia
    # Nota: multiplicamos el puntaje del postulante por cada peso.
    sql = text(f"""
        SELECT
            u.nombre AS universidad,
            c.nombre AS carrera,
            -- puntaje ponderado (mejor entre ciencias o historia)
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

    # Normalizamos a floats redondeados 
    out: List[OpcionPostulacion] = []
    for r in rows:
        out.append(
            OpcionPostulacion(
                universidad=r["universidad"],
                carrera=r["carrera"],
                puntaje_ponderado=float(round(r["puntaje_ponderado"], 2)),
                puntaje_corte=float(round(r["puntaje_corte"], 2)),
                margen=float(round(r["margen"], 2)),
                ano=r["ano"],
            )
        )
    return out