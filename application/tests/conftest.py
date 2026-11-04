"""
Shared test fixtures.
Tests use an in-memory SQLite database so they run without a real MySQL server.
SQLite is compatible enough with our SQLAlchemy models for unit testing.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Use in-memory SQLite for tests — no MySQL required
TEST_DB_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create a single SQLite engine for the whole test session."""
    from app.database import Base
    eng = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def db(engine):
    """Provide a fresh database session per test, rolled back after each test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture()
def client(engine):
    """
    FastAPI TestClient with the database dependency overridden to use SQLite.
    This means every API test hits the same in-memory database.
    """
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

    from app.main import app
    from app.database import get_db

    Session = sessionmaker(bind=engine)

    def override_get_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
