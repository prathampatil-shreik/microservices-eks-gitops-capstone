"""
Shared test fixtures.

Tests use an in-memory SQLite database so they run without a real MySQL server.

Key design decisions
--------------------
StaticPool
    sqlite:///:memory: creates a brand-new empty database for every new
    connection. QueuePool (used in production) opens a new connection per
    session, so the tables created by create_all() would be invisible to the
    session opened inside the request handler. StaticPool forces every
    connect() call to return the same underlying connection object, so all
    sessions share the same in-memory database and the tables are always
    present.

check_same_thread=False
    SQLite's default safety check rejects connections from threads other than
    the one that created them. Starlette's TestClient runs route handlers in a
    worker thread, so this flag must be disabled.

dependency_overrides
    FastAPI resolves get_db() via its dependency injection system on every
    request. We replace it with override_get_db() which returns sessions bound
    to the test engine rather than the production MySQL engine.

lifespan / check_db_connection
    The FastAPI lifespan calls check_db_connection() at startup. That function
    uses the module-level production engine (MySQL). We monkeypatch it to
    return True so no MySQL connection is attempted during tests and the
    startup log stays clean.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """
    Single SQLite engine shared across the entire test session.

    StaticPool is mandatory here: it ensures every SessionLocal() call
    reuses the same underlying connection, so the tables created by
    create_all() are visible to every request handler during the tests.
    """
    from app.database import Base
    # Import models so their table definitions are registered on Base.metadata
    import app.models.task  # noqa: F401

    eng = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def db(engine):
    """
    Provide a fresh database session per test.
    Changes are rolled back after each test so tests do not affect each other.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(engine):
    """
    FastAPI TestClient whose database dependency is overridden to use SQLite.

    Every HTTP request made through this client will use a session bound to
    the in-memory SQLite engine instead of the production MySQL engine.

    check_db_connection is patched to return True so the lifespan startup
    does not attempt a real MySQL connection and does not emit error logs.
    """
    from app.main import app
    from app.database import get_db
    import app.database as db_module

    Session = sessionmaker(bind=engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    # Prevent the lifespan from attempting a real MySQL connection.
    with patch.object(db_module, "check_db_connection", return_value=True):
        with TestClient(app) as c:
            yield c

    app.dependency_overrides.clear()
