"""DealProof FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routers import admin, auth, deals, documents, meta, payments, privacy
from .core.config import settings
from .core.disclaimer import DISCLAIMER


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dev/demo: create tables and seed. Production uses Alembic + a seed command,
    # but this keeps `docker compose up` a single step with a live sample report.
    from .db.base import SessionLocal, create_all

    create_all()
    db = SessionLocal()
    try:
        from .api.demo import bootstrap

        bootstrap(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="DealProofing API",
    version="0.1.0",
    description=DISCLAIMER,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (meta.router, auth.router, deals.router, documents.router, admin.router, payments.router, privacy.router):
    app.include_router(r, prefix="/api")


@app.get("/api")
def root() -> dict:
    return {"service": "dealproof-api", "docs": "/docs", "health": "/api/health"}


@app.get("/api/storage/{key:path}")
def storage_content(key: str, token: str = ""):
    """Serve locally-stored document bytes, gated by a short-lived signed token
    (prod uses presigned S3 URLs). Without a valid token this refuses — the
    documents are the seller's confidential information."""
    from fastapi import HTTPException
    from fastapi.responses import Response

    from .core.security import verify_storage_token
    from .services import storage

    if not verify_storage_token(key, token):
        raise HTTPException(status_code=403, detail="invalid or expired link")
    try:
        data = storage.get_object(key)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="not found")
    return Response(content=data, media_type="application/pdf")


# Serve the built React app (single-service cloud deploy). Mounted last so the
# /api routes above always win; skipped when no build is present (tests/local).
def _mount_frontend() -> None:
    import os

    from fastapi.staticfiles import StaticFiles

    dist = settings.frontend_dist or os.path.join(
        os.path.dirname(__file__), "..", "..", "frontend", "dist"
    )
    if os.path.isdir(dist):
        app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")


_mount_frontend()
