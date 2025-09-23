from typing import Optional, List
from pydantic import BaseModel, Field

# -------- Entradas --------
class SimularRequest(BaseModel):
    ano: int = Field(..., ge=2000, le=2100)
    lenguaje: float
    matematicas: float
    matematicas2: float
    ciencias: float
    historia: float
    nem: float
    ranking: float
    universidad: Optional[str] = None  # filtro "contiene"
    carrera: Optional[str] = None      # filtro "contiene"
    limit: int = 30

# -------- Salidas --------
class OpcionPostulacion(BaseModel):
    universidad: str
    carrera: str
    puntaje_corte: float
    puntaje_ponderado: float
    margen: float  # ponderado - corte

# para endpoints de catálogo
class UniversidadOut(BaseModel):
    id: int
    nombre: str
    acreditacion: Optional[int] = None
    sitio_web: Optional[str] = None
    direccion: Optional[str] = None
    class Config:
        from_attributes = True