"""
Application configuration loaded from environment variables.
All sensitive values (passwords, secrets) must be set via environment variables.
Never hardcode credentials here.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "MicroTask API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # MySQL — all values come from environment variables
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DATABASE: str = "microtask_db"
    MYSQL_USER: str = "microtask_user"
    MYSQL_PASSWORD: str = ""

    # Connection pool settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800  # Recycle connections every 30 min (important for RDS)

    # CORS — comma-separated list of allowed origins
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @property
    def DATABASE_URL(self) -> str:
        """Build the SQLAlchemy MySQL connection URL."""
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True
        # Ignore environment variables that are not declared as fields.
        # This is required because the same environment may contain worker
        # variables (WORKER_NAME, FAILURE_RATE, etc.) that belong to the
        # worker service, not the API. Pydantic v2 defaults to 'forbid'.
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Cache settings so environment is only read once."""
    return Settings()
