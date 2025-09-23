from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

# =======================
#   Universidades
# =======================
class Universidad(Base):
    __tablename__ = "universidades"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    acreditacion = Column(Integer, nullable=True)
    sitio_web = Column(String(255), nullable=True)
    direccion = Column(String(255), nullable=True)
    latitud = Column(DECIMAL(10, 7), nullable=True)
    longitud = Column(DECIMAL(10, 7), nullable=True)

    carreras = relationship("Carrera", back_populates="universidad")


# =======================
#   Carreras
# =======================
class Carrera(Base):
    __tablename__ = "carreras"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(120), nullable=False)
    duracion = Column(String(50), nullable=True)
    vacantes = Column(Integer, nullable=True)
    arancel = Column(Integer, nullable=True)
    universidad_id = Column(Integer, ForeignKey("universidades.id"), nullable=False)

    universidad = relationship("Universidad", back_populates="carreras")
    puntajes = relationship("PuntajeCorte", back_populates="carrera")
    # relación 1–1 (o 1–0/1) con ponderaciones
    ponderacion = relationship("Ponderacion", uselist=False, back_populates="carrera")


# =======================
#   Puntajes de corte
# =======================
class PuntajeCorte(Base):
    __tablename__ = "puntajes_corte"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False)
    puntaje_minimo = Column(DECIMAL(6, 2), nullable=False)
    ano = Column(Integer, nullable=False)

    carrera = relationship("Carrera", back_populates="puntajes")


# =======================
#   Simulaciones (histórico opcional)
# =======================
class Simulacion(Base):
    __tablename__ = "simulaciones"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=True)
    puntaje_lenguaje = Column(DECIMAL(5, 2), nullable=True)
    puntaje_matematicas = Column(DECIMAL(5, 2), nullable=True)
    puntaje_matematicas2 = Column(DECIMAL(5, 2), nullable=True)
    puntaje_ciencias = Column(DECIMAL(5, 2), nullable=True)
    puntaje_historia = Column(DECIMAL(5, 2), nullable=True)
    puntaje_historia_electiva = Column(DECIMAL(5, 2), nullable=True)
    puntaje_nem = Column(DECIMAL(5, 2), nullable=True)
    puntaje_ranking = Column(DECIMAL(5, 2), nullable=True)
    puntaje_total = Column(DECIMAL(5, 2), nullable=False)


# =======================
#   Ponderaciones por carrera 
# =======================
class Ponderacion(Base):
    __tablename__ = "ponderaciones"

    id = Column(Integer, primary_key=True, index=True)
    carrera_id = Column(Integer, ForeignKey("carreras.id"), nullable=False, unique=True)

    # pesos (suman aprox 1.0)
    w_lenguaje = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_matematicas = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_matematicas2 = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_ciencias = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_historia = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_nem = Column(DECIMAL(5, 4), nullable=False, default=0)
    w_ranking = Column(DECIMAL(5, 4), nullable=False, default=0)

    carrera = relationship("Carrera", back_populates="ponderacion")
