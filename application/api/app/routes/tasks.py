"""
Task CRUD routes — all endpoints under /api/v1/tasks
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskCreate, TaskUpdate, TaskResponse,
    TaskDetailResponse, TaskHistoryResponse,
    StatsResponse, PaginatedTaskResponse,
)
from app.services import task_service

router = APIRouter(prefix="/api/v1", tags=["tasks"])


@router.get("/tasks", response_model=PaginatedTaskResponse)
def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search title/description"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    items, total, total_pages = task_service.get_tasks(
        db, status=status, search=search, page=page, page_size=page_size
    )
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    return task_service.create_task(db, payload)


@router.get("/tasks/{task_id}", response_model=TaskDetailResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task(db, task_id)


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    return task_service.update_task(db, task_id, payload)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service.delete_task(db, task_id)


@router.get("/tasks/{task_id}/history", response_model=list[TaskHistoryResponse])
def get_task_history(task_id: int, db: Session = Depends(get_db)):
    return task_service.get_task_history(db, task_id)


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    return task_service.get_stats(db)
