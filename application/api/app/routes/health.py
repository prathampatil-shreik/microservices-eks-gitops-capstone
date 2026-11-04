"""
Health check endpoints.
/health/live  — Kubernetes liveness probe  (is the process running?)
/health/ready — Kubernetes readiness probe (can it serve traffic?)
/health       — Combined check for convenience
"""
from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.database import check_db_connection
from app.config import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
def health():
    db_ok = check_db_connection()
    payload = {
        "status": "healthy" if db_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_ok else "disconnected",
    }
    code = 200 if db_ok else 503
    return JSONResponse(content=payload, status_code=code)


@router.get("/health/live")
def liveness():
    """Liveness: just confirm the process is alive."""
    return {"status": "alive"}


@router.get("/health/ready")
def readiness():
    """Readiness: confirm the app can reach the database."""
    db_ok = check_db_connection()
    if not db_ok:
        return JSONResponse(
            content={"status": "not ready", "reason": "database unreachable"},
            status_code=503,
        )
    return {"status": "ready"}
