from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 -- register models for create_all
from app.routes import auth, kegiatan, lamaran, logbook, mahasiswa, mitra, notifikasi


app = FastAPI(title=settings.app_name, version="0.1.0")

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# Izinkan React (Vite default port 5173, CRA port 3000) untuk konsumsi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/", tags=["root"])
def root() -> dict:
    return {"app": settings.app_name, "status": "ok", "docs": "/docs"}


# Register semua routers
app.include_router(auth.router)
app.include_router(mahasiswa.router)
app.include_router(mitra.router)
app.include_router(kegiatan.router)
app.include_router(lamaran.router)
app.include_router(logbook.router)
app.include_router(notifikasi.router)
