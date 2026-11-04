"""
Unit tests for the task service layer and worker processor.
These tests call service functions directly, bypassing HTTP.
"""
import pytest
from unittest.mock import patch
from app.models.task import TaskStatus, TaskPriority, TaskType
from app.schemas.task import TaskCreate, TaskUpdate
from app.services import task_service


# ── Service layer tests ────────────────────────────────────────────────────────

def test_create_task_service(db):
    payload = TaskCreate(
        title="Service Test Task",
        task_type=TaskType.DATA_PROCESSING,
        priority=TaskPriority.HIGH,
    )
    task = task_service.create_task(db, payload)
    assert task.id is not None
    assert task.status == TaskStatus.PENDING
    assert task.title == "Service Test Task"


def test_create_task_adds_history_entry(db):
    payload = TaskCreate(title="History Test", task_type=TaskType.CLEANUP, priority=TaskPriority.LOW)
    task = task_service.create_task(db, payload)
    history = task_service.get_task_history(db, task.id)
    assert len(history) == 1
    assert history[0].current_status == "PENDING"
    assert history[0].previous_status is None


def test_update_task_status_adds_history(db):
    payload = TaskCreate(title="Update Test", task_type=TaskType.FILE_EXPORT, priority=TaskPriority.MEDIUM)
    task = task_service.create_task(db, payload)

    task_service.update_task(db, task.id, TaskUpdate(status=TaskStatus.COMPLETED))
    history = task_service.get_task_history(db, task.id)

    statuses = [h.current_status for h in history]
    assert "COMPLETED" in statuses


def test_get_stats_returns_correct_counts(db):
    # Create tasks with known statuses
    for _ in range(2):
        task_service.create_task(db, TaskCreate(title="P", task_type=TaskType.CLEANUP, priority=TaskPriority.LOW))

    stats = task_service.get_stats(db)
    assert stats["pending"] >= 2
    assert stats["total"] >= 2


def test_delete_task_removes_from_db(db):
    from fastapi import HTTPException
    payload = TaskCreate(title="Delete Me", task_type=TaskType.CLEANUP, priority=TaskPriority.LOW)
    task = task_service.create_task(db, payload)
    task_id = task.id

    task_service.delete_task(db, task_id)

    with pytest.raises(HTTPException) as exc_info:
        task_service.get_task(db, task_id)
    assert exc_info.value.status_code == 404


def test_get_task_not_found_raises_404(db):
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as exc_info:
        task_service.get_task(db, 999999)
    assert exc_info.value.status_code == 404


# ── Worker processor tests ─────────────────────────────────────────────────────

def test_processor_returns_success():
    """Processor returns a success dict when no failure is triggered."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))

    from processor import process_task
    from config import config

    # Force success by setting failure rate to 0
    with patch.object(config, "FAILURE_RATE", 0.0), \
         patch.object(config, "MIN_PROCESSING_SECONDS", 0.01), \
         patch.object(config, "MAX_PROCESSING_SECONDS", 0.02):
        result = process_task(1, "DATA_PROCESSING", "Test Task")

    assert result["success"] is True
    assert "message" in result
    assert result["duration_seconds"] > 0


def test_processor_raises_on_failure():
    """Processor raises RuntimeError when failure is triggered."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))

    from processor import process_task
    from config import config

    with patch.object(config, "FAILURE_RATE", 1.0), \
         patch.object(config, "MIN_PROCESSING_SECONDS", 0.01), \
         patch.object(config, "MAX_PROCESSING_SECONDS", 0.02):
        with pytest.raises(RuntimeError):
            process_task(1, "DATA_PROCESSING", "Failing Task")


def test_processor_handles_all_task_types():
    """Processor accepts all valid task types without error."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "worker"))

    from processor import process_task
    from config import config

    task_types = ["DATA_PROCESSING", "REPORT_GENERATION", "EMAIL_NOTIFICATION", "FILE_EXPORT", "CLEANUP"]

    with patch.object(config, "FAILURE_RATE", 0.0), \
         patch.object(config, "MIN_PROCESSING_SECONDS", 0.01), \
         patch.object(config, "MAX_PROCESSING_SECONDS", 0.02):
        for t in task_types:
            result = process_task(1, t, f"Task of type {t}")
            assert result["success"] is True
