"""
MicroTask Background Worker
============================
This worker continuously polls MySQL for PENDING tasks and processes them.

Key design decisions:
- SELECT ... FOR UPDATE SKIP LOCKED: MySQL-native row-level locking that lets
  multiple worker instances run simultaneously without processing the same task twice.
- Heartbeat: the worker updates its last_heartbeat timestamp so the API can
  detect dead workers.
- Retry: failed tasks are retried up to MAX_RETRIES times before being marked FAILED.
"""
import logging
import signal
import sys
import time
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from config import config
from database import get_session
from processor import process_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger("microtask.worker")

# ── Graceful shutdown ─────────────────────────────────────────────────────────
_running = True


def _handle_signal(signum, frame):
    global _running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    _running = False


signal.signal(signal.SIGTERM, _handle_signal)
signal.signal(signal.SIGINT, _handle_signal)


# ── Worker registration ───────────────────────────────────────────────────────

def register_worker(session) -> None:
    """Insert or update this worker's row in the workers table."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            INSERT INTO workers (worker_name, status, last_heartbeat, created_at)
            VALUES (:name, 'IDLE', :now, :now)
            ON DUPLICATE KEY UPDATE status='IDLE', last_heartbeat=:now
        """),
        {"name": config.WORKER_NAME, "now": now},
    )
    session.commit()
    logger.info(f"Worker registered: {config.WORKER_NAME}")


def update_heartbeat(session, status: str = "IDLE") -> None:
    """Update the worker's heartbeat timestamp and status."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            UPDATE workers
            SET last_heartbeat = :now, status = :status
            WHERE worker_name = :name
        """),
        {"now": now, "status": status, "name": config.WORKER_NAME},
    )
    session.commit()


# ── Task claiming ─────────────────────────────────────────────────────────────

def claim_next_task(session):
    """
    Atomically claim the next PENDING task.

    SELECT ... FOR UPDATE SKIP LOCKED is the key MySQL feature here:
    - FOR UPDATE: locks the selected row so no other transaction can modify it
    - SKIP LOCKED: if a row is already locked by another worker, skip it
    This allows multiple workers to run in parallel safely.
    """
    row = session.execute(
        text("""
            SELECT id, title, task_type, status
            FROM tasks
            WHERE status = 'PENDING'
            ORDER BY
                CASE priority WHEN 'HIGH' THEN 1 WHEN 'MEDIUM' THEN 2 ELSE 3 END,
                created_at ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        """)
    ).fetchone()

    if not row:
        return None

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            UPDATE tasks
            SET status = 'PROCESSING', started_at = :now, updated_at = :now
            WHERE id = :id
        """),
        {"now": now, "id": row.id},
    )
    session.execute(
        text("""
            INSERT INTO task_history (task_id, previous_status, current_status, message, created_at)
            VALUES (:task_id, 'PENDING', 'PROCESSING', :msg, :now)
        """),
        {
            "task_id": row.id,
            "msg": f"Claimed by worker {config.WORKER_NAME}",
            "now": now,
        },
    )
    session.commit()
    return row


def mark_completed(session, task_id: int, message: str) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            UPDATE tasks
            SET status = 'COMPLETED', completed_at = :now, updated_at = :now
            WHERE id = :id
        """),
        {"now": now, "id": task_id},
    )
    session.execute(
        text("""
            INSERT INTO task_history (task_id, previous_status, current_status, message, created_at)
            VALUES (:task_id, 'PROCESSING', 'COMPLETED', :msg, :now)
        """),
        {"task_id": task_id, "msg": message, "now": now},
    )
    session.commit()


def mark_failed(session, task_id: int, error: str) -> None:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            UPDATE tasks
            SET status = 'FAILED', updated_at = :now
            WHERE id = :id
        """),
        {"now": now, "id": task_id},
    )
    session.execute(
        text("""
            INSERT INTO task_history (task_id, previous_status, current_status, message, created_at)
            VALUES (:task_id, 'PROCESSING', 'FAILED', :msg, :now)
        """),
        {"task_id": task_id, "msg": f"Failed: {error}", "now": now},
    )
    session.commit()


def requeue_task(session, task_id: int, attempt: int) -> None:
    """Put a failed task back to PENDING for retry."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    session.execute(
        text("""
            UPDATE tasks
            SET status = 'PENDING', updated_at = :now
            WHERE id = :id
        """),
        {"now": now, "id": task_id},
    )
    session.execute(
        text("""
            INSERT INTO task_history (task_id, previous_status, current_status, message, created_at)
            VALUES (:task_id, 'PROCESSING', 'PENDING', :msg, :now)
        """),
        {
            "task_id": task_id,
            "msg": f"Requeued for retry (attempt {attempt}/{config.MAX_RETRIES})",
            "now": now,
        },
    )
    session.commit()


def get_retry_count(session, task_id: int) -> int:
    """Count how many times this task has been retried."""
    row = session.execute(
        text("""
            SELECT COUNT(*) as cnt FROM task_history
            WHERE task_id = :id AND current_status = 'PENDING'
            AND message LIKE 'Requeued%'
        """),
        {"id": task_id},
    ).fetchone()
    return row.cnt if row else 0


# ── Main loop ─────────────────────────────────────────────────────────────────

def wait_for_db(max_attempts: int = 30) -> None:
    """Block until the database is reachable. Retries every 2 seconds."""
    from sqlalchemy import text as t
    from database import engine

    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as conn:
                conn.execute(t("SELECT 1"))
            logger.info("Database connection established")
            return
        except OperationalError as e:
            logger.warning(f"DB not ready (attempt {attempt}/{max_attempts}): {e}")
            time.sleep(2)
    logger.error("Could not connect to database after maximum attempts. Exiting.")
    sys.exit(1)


def run():
    logger.info(f"MicroTask Worker starting — name={config.WORKER_NAME}")
    wait_for_db()

    session = get_session()
    register_worker(session)

    last_heartbeat = time.time()

    while _running:
        try:
            # Periodic heartbeat
            if time.time() - last_heartbeat >= config.HEARTBEAT_INTERVAL_SECONDS:
                update_heartbeat(session, "IDLE")
                last_heartbeat = time.time()

            task = claim_next_task(session)

            if task is None:
                time.sleep(config.POLL_INTERVAL_SECONDS)
                continue

            logger.info(f"Processing task id={task.id} type={task.task_type} title='{task.title}'")
            update_heartbeat(session, "BUSY")

            try:
                result = process_task(task.id, task.task_type, task.title)
                mark_completed(session, task.id, result["message"])
                logger.info(f"Task {task.id} COMPLETED in {result['duration_seconds']:.1f}s")

            except Exception as e:
                retry_count = get_retry_count(session, task.id)
                if retry_count < config.MAX_RETRIES:
                    logger.warning(f"Task {task.id} failed (retry {retry_count + 1}/{config.MAX_RETRIES}): {e}")
                    requeue_task(session, task.id, retry_count + 1)
                else:
                    logger.error(f"Task {task.id} FAILED after {config.MAX_RETRIES} retries: {e}")
                    mark_failed(session, task.id, str(e))

            update_heartbeat(session, "IDLE")
            last_heartbeat = time.time()

        except OperationalError as e:
            logger.error(f"Database error in main loop: {e}")
            time.sleep(5)
            try:
                session.rollback()
            except Exception:
                pass

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            time.sleep(5)

    logger.info("Worker stopped")
    session.close()


if __name__ == "__main__":
    run()
