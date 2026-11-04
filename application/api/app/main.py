"""
MicroTask FastAPI application entry point.
This file wires together all routes, middleware and startup logic.
"""
import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import engine, check_db_connection
from app.models.task import Task, TaskHistory, Worker  # noqa: F401 — needed for Base.metadata
from app.database import Base
from app.routes import tasks, health, metrics
from app.middleware.logging_middleware import RequestLoggingMiddleware

settings = get_settings()

# ── Logging configuration ─────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Code here runs once at startup (before 'yield') and once at shutdown (after).
    We verify the database is reachable when the API starts.
    """
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    if check_db_connection():
        logger.info("Database connection verified")
    else:
        logger.warning("Database not reachable at startup — will retry on requests")
    yield
    logger.info("Shutting down gracefully")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="MicroTask — background task management API",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────────────────

app.include_router(health.router)
app.include_router(tasks.router)
app.include_router(metrics.router)


@app.get("/", tags=["root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
