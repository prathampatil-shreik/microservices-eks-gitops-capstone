"""
Alembic environment configuration.
This file tells Alembic how to connect to the database and where to find models.
It reads the database URL from environment variables so credentials are never
stored in source code.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Add the api directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base
from app.models import task  # noqa: F401 — import models so Alembic sees them

config = context.config
fileConfig(config.config_file_name)

# Build the database URL from environment variables
def get_url():
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    db = os.getenv("MYSQL_DATABASE", "microtask_db")
    user = os.getenv("MYSQL_USER", "microtask_user")
    password = os.getenv("MYSQL_PASSWORD", "")
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"


target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations without a live database connection (generates SQL scripts)."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations against a live database connection."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
