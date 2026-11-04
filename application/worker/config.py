"""Worker configuration from environment variables."""
import os


class WorkerConfig:
    # Database
    MYSQL_HOST: str = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT: int = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE: str = os.getenv("MYSQL_DATABASE", "microtask_db")
    MYSQL_USER: str = os.getenv("MYSQL_USER", "microtask_user")
    MYSQL_PASSWORD: str = os.getenv("MYSQL_PASSWORD", "")

    # Worker behaviour
    WORKER_NAME: str = os.getenv("WORKER_NAME", "worker-1")
    POLL_INTERVAL_SECONDS: float = float(os.getenv("POLL_INTERVAL_SECONDS", "5"))
    HEARTBEAT_INTERVAL_SECONDS: float = float(os.getenv("HEARTBEAT_INTERVAL_SECONDS", "15"))

    # Processing simulation
    MIN_PROCESSING_SECONDS: float = float(os.getenv("MIN_PROCESSING_SECONDS", "2"))
    MAX_PROCESSING_SECONDS: float = float(os.getenv("MAX_PROCESSING_SECONDS", "8"))

    # Set FAILURE_RATE=0.2 to make 20% of tasks fail (useful for testing alerts)
    FAILURE_RATE: float = float(os.getenv("FAILURE_RATE", "0.1"))

    # Retry
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )


config = WorkerConfig()
