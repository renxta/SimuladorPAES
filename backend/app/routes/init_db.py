from app.db import Base, engine
from app import models

print("Creando tablas en la base de datos...")
Base.metadata.create_all(bind=engine)
print("¡Listo! Tablas creadas.")
