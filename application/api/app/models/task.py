"""
SQLAlchemy ORM models for the MicroTask application.
These classes map directly to MySQL tables.
"""
import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Enum,
    ForeignKey, Index
)
from sqlalchemy.orm import relationship

from app.database import Base


def utcnow():
    """Return current UTC time. Used as default for timestamp columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TaskStatus(str, enum.Enum):
    """All possible states a task can be in."""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TaskType(str, enum.Enum):
    DATA_PROCESSING = "DATA_PROCESSING"
    REPORT_GENERATION = "REPORT_GENERATION"
    EMAIL_NOTIFICATION = "EMAIL_NOTIFICATION"
    FILE_EXPORT = "FILE_EXPORT"
    CLEANUP = "CLEANUP"


class Task(Base):
    """
    Main tasks table.
    Each row represents one background job submitted by the user.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    task_type = Column(
        Enum(TaskType),
        nullable=False,
        default=TaskType.DATA_PROCESSING
    )
    priority = Column(
        Enum(TaskPriority),
        nullable=False,
        default=TaskPriority.MEDIUM
    )
    status = Column(
        Enum(TaskStatus),
        nullable=False,
        default=TaskStatus.PENDING,
        index=True  # Indexed because the worker queries by status frequently
    )
    created_at = Column(DateTime, nullable=False, default=utcnow)
    updated_at = Column(DateTime, nullable=False, default=utcnow, onupdate=utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # One task has many history entries
    history = relationship(
        "TaskHistory",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskHistory.created_at"
    )

    __table_args__ = (
        # Composite index for common query: filter by status, order by created_at
        Index("ix_tasks_status_created", "status", "created_at"),
    )


class TaskHistory(Base):
    """
    Audit log for every status change on a task.
    Lets users see the full processing timeline.
    """
    __tablename__ = "task_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(
        Integer,
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    previous_status = Column(String(50), nullable=True)
    current_status = Column(String(50), nullable=False)
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)

    task = relationship("Task", back_populates="history")


class Worker(Base):
    """
    Registry of active background worker processes.
    Workers update last_heartbeat periodically so we can detect dead workers.
    """
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    worker_name = Column(String(255), nullable=False, unique=True)
    status = Column(String(50), nullable=False, default="IDLE")
    last_heartbeat = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utcnow)
