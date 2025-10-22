# app/routes/simulador.py
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..db import get_db
from .. import schemas

router = APIRouter(prefix="/simular", tags=["simulador"])

@router.post("/", response_model=List[schemas.OpcionPostulacion])
def simular(req: schemas.SimularRequest, db: Session = Depends(get_db)):
    """
    Calcula puntaje ponderado por carrera según 'ponderaciones'
    y lo compara con el puntaje de corte del año solicitado.
    Permite filtrar por nombre de universidad/carrera (contiene).
    """
    sql = text("""
        SELECT
            u.nombre                           AS universidad,
            c.nombre                           AS carrera,
            -- ponderado = suma(peso_i * puntaje_usuario_i)
            (
                :lenguaje  * p.w_lenguaje     +
                :mat1      * p.w_matematicas  +
                :mat2      * p.w_matematicas2 +
                GREATEST(:ciencias, :historia) * GREATEST(p.w_ciencias, p.w_historia) +
                :nem       * p.w_nem          +
                :ranking   * p.w_ranking
            )                                   AS puntaje_ponderado,
            COALESCE(pc.puntaje_minimo, 0)      AS puntaje_corte,
            (
                (
                    :lenguaje  * p.w_lenguaje     +
                    :mat1      * p.w_matematicas  +
                    :mat2      * p.w_matematicas2 +
                    GREATEST(:ciencias, :historia) * GREATEST(p.w_ciencias, p.w_historia) +
                    :nem       * p.w_nem          +
                    :ranking   * p.w_ranking
                ) - COALESCE(pc.puntaje_minimo, 0)
            )                                   AS margen
        FROM ponderaciones p
        JOIN carreras c       ON c.id = p.carrera_id
        JOIN universidades u  ON u.id = c.universidad_id
        LEFT JOIN puntajes_corte pc ON pc.carrera_id = c.id AND pc.ano = :ano
        WHERE
            (:f_uni IS NULL OR u.nombre LIKE CONCAT('%', :f_uni, '%'))
        AND (:f_car IS NULL OR c.nombre LIKE CONCAT('%', :f_car, '%'))
        ORDER BY margen DESC, u.nombre, c.nombre
        LIMIT 200
    """)

    params = {
        "ano": req.ano,
        "lenguaje": req.lenguaje,
        "mat1": req.matematicas,
        "mat2": req.matematicas2,
        "ciencias": req.ciencias,
        "historia": req.historia,
        "nem": req.nem,
        "ranking": req.ranking,
        "f_uni": req.universidad if (req.universidad and req.universidad.strip()) else None,
        "f_car": req.carrera if (req.carrera and req.carrera.strip()) else None,
    }

    rows = db.execute(sql, params).mappings().all()

    # Opcional: si quieres mostrar solo las que alcanza, descomenta:
    # rows = [r for r in rows if r["margen"] >= 0]

    return [
        schemas.OpcionPostulacion(
            universidad=r["universidad"],
            carrera=r["carrera"],
            puntaje_ponderado=float(r["puntaje_ponderado"]),
            puntaje_corte=float(r["puntaje_corte"]),
            margen=float(r["margen"]),
        )
        for r in rows
    ]