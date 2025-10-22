# app/models.py
from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

# --------------------------
# UNIVERSIDADES
# --------------------------
class Universidad(Base):
    __tablename__ = "universidades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False, unique=True)
    acreditacion = Column(Integer, nullable=True)  # 1 si acreditada, 0 si no
    sitio_web = Column(String(255))
    direccion = Column(String(255))
    latitud = Column(DECIMAL(10,7))
    longitud = Column(DECIMAL(10,7))

    carreras = relationship("Carrera", back_populates="universidad")


# --------------------------
# CARRERAS
# --------------------------
class Carrera(Base):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(150), nullable=False)
    vacantes = Column(Integer)
    arancel = Column(Integer)
    universidad_id = Column(Integer, ForeignKey("universidades.id"), nullable=False)

    universidad = relationship("Universidad", back_populates="carreras")
    ponderacion = relationship("Ponderacion", uselist=False, back_populates="carrera")
    puntajes = relationship("PuntajeCorte", back_populates="carrera")
    simulaciones = relationship("Simulacion", back_populates="carrera")


# --------------------------
# PONDERACIONES
# --------------------------
class Ponderacion(Base):
    __tablename__ = "ponderaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False, unique=True)

    w_lenguaje = Column(DECIMAL(5,4), default=0)
    w_matematicas = Column(DECIMAL(5,4), default=0)
    w_matematicas2 = Column(DECIMAL(5,4), default=0)
    w_ciencias = Column(DECIMAL(5,4), default=0)
    w_historia = Column(DECIMAL(5,4), default=0)
    w_nem = Column(DECIMAL(5,4), default=0)
    w_ranking = Column(DECIMAL(5,4), default=0)

    carrera = relationship("Carrera", back_populates="ponderacion")


# --------------------------
# PUNTAJES DE CORTE
# --------------------------
class PuntajeCorte(Base):
    __tablename__ = "puntajes_corte"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False)
    puntaje_minimo = Column(DECIMAL(6,2), nullable=False)
    ano = Column(Integer, nullable=False)

    carrera = relationship("Carrera", back_populates="puntajes")


# --------------------------
# SIMULACIONES (histórico)
# --------------------------
class Simulacion(Base):
    __tablename__ = "simulaciones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"))
    puntaje_lenguaje = Column(DECIMAL(5,2))
    puntaje_matematicas = Column(DECIMAL(5,2))
    puntaje_matematicas2 = Column(DECIMAL(5,2))
    puntaje_ciencias = Column(DECIMAL(5,2))
    puntaje_historia = Column(DECIMAL(5,2))
    puntaje_nem = Column(DECIMAL(5,2))
    puntaje_ranking = Column(DECIMAL(5,2))
    puntaje_total = Column(DECIMAL(6,2), nullable=False)

    carrera = relationship("Carrera", back_populates="simulaciones")
