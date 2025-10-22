from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import simulador

app = FastAPI(
    title="Simulador PAES API",
    version="1.0.0",
    contact={"name": "Simulador PAES"},
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas
app.include_router(simulador.router)  

# Endpoints base de verificación
@app.get("/", tags=["default"])
def root():
    return {"ok": True, "msg": "Simulador PAES API"}

@app.get("/health", tags=["default"])
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)