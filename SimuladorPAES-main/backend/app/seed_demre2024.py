# app/seed_demre2024.py
import pandas as pd
from sqlalchemy.orm import Session
from app.db import engine
from app import models
import sys

# Forzar UTF-8 global
sys.stdout.reconfigure(encoding='utf-8')
#  Ruta del archivo Excel DEMRE 2024
file_path = r"C:\Users\usuario\Documents\SimuladorPAES-main\SimuladorPAES-main\backend\OfertaAcadémica_Admisión2024.xlsx"

# Leer archivo Excel
df = pd.read_excel(file_path)
df = df.fillna(0)

def clean_text(x):
    return str(x).strip().title() if isinstance(x, str) else x

session = Session(bind=engine)
universidades_cache = {}

for _, row in df.iterrows():
    uni_nombre = clean_text(row["NOMBRE_UNIVERSIDAD"])
    carrera_nombre = clean_text(row["NOMBRE_CARRERA"])
    if not uni_nombre or not carrera_nombre:
        continue

    # ---------------------------------------
    # UNIVERSIDAD
    # ---------------------------------------
    if uni_nombre not in universidades_cache:
        uni = session.query(models.Universidad).filter_by(nombre=uni_nombre).first()
        if not uni:
            acreditada = 1 if str(row["ACREDITADA_3AHNOS"]).strip().upper() == "S" else 0
            uni = models.Universidad(nombre=uni_nombre, acreditacion=acreditada)
            session.add(uni)
            session.flush()
        universidades_cache[uni_nombre] = uni.id
    uni_id = universidades_cache[uni_nombre]

    # ---------------------------------------
    # CARRERA
    # ---------------------------------------
    carrera = (
        session.query(models.Carrera)
        .filter_by(nombre=carrera_nombre, universidad_id=uni_id)
        .first()
    )
    if not carrera:
        carrera = models.Carrera(
            nombre=carrera_nombre,
            universidad_id=uni_id,
            vacantes=int(row["VACANTES_1SEM"]) if row["VACANTES_1SEM"] else None,
        )
        session.add(carrera)
        session.flush()

    # ---------------------------------------
    # PONDERACIONES (evitar duplicados)
    # ---------------------------------------
    existe_ponderacion = session.query(models.Ponderacion).filter_by(carrera_id=carrera.id).first()
    if not existe_ponderacion:
        ponderacion = models.Ponderacion(
            carrera_id=carrera.id,
            w_lenguaje=row["%_LENG"] / 100,
            w_matematicas=row["%_MATE1"] / 100,
            w_matematicas2=row["%_MATE2"] / 100,
            w_ciencias=row["%_CIEN"] / 100,
            w_historia=row["%_HYCS"] / 100,
            w_nem=row["%_NOTAS"] / 100,
            w_ranking=row["%_Ranking"] / 100,
        )
        session.add(ponderacion)
    else:
        # Ya existe ponderación → no se agrega otra
        pass

    # ---------------------------------------
    # PUNTAJE DE CORTE (evitar duplicados)
    # ---------------------------------------
    if row["PONDERADO_MINIMO"] and row["PONDERADO_MINIMO"] > 0:
        existe_corte = session.query(models.PuntajeCorte).filter_by(
            carrera_id=carrera.id, ano=2024
        ).first()
        if not existe_corte:
            corte = models.PuntajeCorte(
                carrera_id=carrera.id,
                puntaje_minimo=row["PONDERADO_MINIMO"],
                ano=2024,
            )
            session.add(corte)

# ---------------------------------------
# COMMIT FINAL
# ---------------------------------------
session.commit()
session.close()
print("Datos DEMRE 2024 cargados exitosamente.")
