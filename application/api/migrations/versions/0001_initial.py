"""Initial schema — create tasks, task_history and workers tables

Revision ID: 0001_initial
Revises:
Create Date: 2024-01-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ── tasks ─────────────────────────────────────────────────────────────────
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "task_type",
            sa.Enum(
                "DATA_PROCESSING", "REPORT_GENERATION",
                "EMAIL_NOTIFICATION", "FILE_EXPORT", "CLEANUP",
                name="tasktype",
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.Enum("LOW", "MEDIUM", "HIGH", name="taskpriority"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PROCESSING", "COMPLETED", "FAILED", name="taskstatus"),
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_status_created", "tasks", ["status", "created_at"])

    # ── task_history ──────────────────────────────────────────────────────────
    op.create_table(
        "task_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("previous_status", sa.String(50), nullable=True),
        sa.Column("current_status", sa.String(50), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )
    op.create_index("ix_task_history_task_id", "task_history", ["task_id"])

    # ── workers ───────────────────────────────────────────────────────────────
    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("worker_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="IDLE"),
        sa.Column("last_heartbeat", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("worker_name"),
        mysql_engine="InnoDB",
        mysql_charset="utf8mb4",
    )


def downgrade():
    op.drop_table("workers")
    op.drop_table("task_history")
    op.drop_table("tasks")
