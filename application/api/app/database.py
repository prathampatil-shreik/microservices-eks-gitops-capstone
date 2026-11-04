"""
Database connection management using SQLAlchemy.
Creates the engine, session factory and Base class used by all models.
"""
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy.pool import QueuePool
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# SQLAlchemy engine — QueuePool handles connection reuse efficiently
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    pool_pre_ping=True,   # Verify connection is alive before using it
    echo=settings.DEBUG,  # Log SQL queries only in debug mode
)


# Session factory — each request gets its own session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class that all SQLAlchemy models inherit from."""
    pass


def get_db():
    """
    FastAPI dependency that provides a database session per request.
    The session is automatically closed when the request finishes,
    even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Test the database connection. Used by health check endpoints."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False
