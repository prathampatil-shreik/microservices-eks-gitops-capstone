"""
Business logic layer — all database operations for tasks live here.
Routes call these functions; they never touch the DB directly.
This separation makes the code easier to test and maintain.
"""
import logging
import math
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.task import Task, TaskHistory, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


def _add_history(
    db: Session,
    task_id: int,
    previous_status: Optional[str],
    current_status: str,
    message: str,
):
    """Insert a row into task_history. Called whenever a task status changes."""
    entry = TaskHistory(
        task_id=task_id,
        previous_status=previous_status,
        current_status=current_status,
        message=message,
    )
    db.add(entry)


def get_tasks(
    db: Session,
    status: Optional[TaskStatus] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    query = db.query(Task)

    if status:
        query = query.filter(Task.status == status)

    if search:
        like = f"%{search}%"
        query = query.filter(
            Task.title.ilike(like) | Task.description.ilike(like)
        )

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    items = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return items, total, total_pages


def get_task(db: Session, task_id: int) -> Task:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


def create_task(db: Session, payload: TaskCreate) -> Task:
    task = Task(
        title=payload.title,
        description=payload.description,
        task_type=payload.task_type,
        priority=payload.priority,
        status=TaskStatus.PENDING,
    )
    db.add(task)
    db.flush()  # Get the auto-generated id before committing

    _add_history(
        db, task.id,
        previous_status=None,
        current_status=TaskStatus.PENDING,
        message="Task created and queued for processing",
    )

    db.commit()
    db.refresh(task)
    logger.info(f"Task created: id={task.id} title='{task.title}'")
    return task


def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Task:
    task = get_task(db, task_id)
    old_status = task.status

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    if "status" in update_data and update_data["status"] != old_status:
        _add_history(
            db, task.id,
            previous_status=old_status,
            current_status=update_data["status"],
            message=f"Status manually updated via API",
        )

    db.commit()
    db.refresh(task)
    logger.info(f"Task updated: id={task.id}")
    return task


def delete_task(db: Session, task_id: int) -> None:
    task = get_task(db, task_id)
    db.delete(task)
    db.commit()
    logger.info(f"Task deleted: id={task_id}")


def get_task_history(db: Session, task_id: int):
    get_task(db, task_id)  # Raises 404 if task doesn't exist
    return (
        db.query(TaskHistory)
        .filter(TaskHistory.task_id == task_id)
        .order_by(TaskHistory.created_at.asc())
        .all()
    )


def get_stats(db: Session) -> dict:
    rows = (
        db.query(Task.status, func.count(Task.id))
        .group_by(Task.status)
        .all()
    )
    counts = {row[0]: row[1] for row in rows}
    total = sum(counts.values())
    return {
        "total": total,
        "pending": counts.get(TaskStatus.PENDING, 0),
        "processing": counts.get(TaskStatus.PROCESSING, 0),
        "completed": counts.get(TaskStatus.COMPLETED, 0),
        "failed": counts.get(TaskStatus.FAILED, 0),
    }
