"""
Pydantic schemas for request validation and response serialization.
Pydantic ensures incoming JSON is valid before it touches the database.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.task import TaskStatus, TaskPriority, TaskType


# ── Request schemas (what the client sends) ──────────────────────────────────

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000)
    task_type: TaskType = TaskType.DATA_PROCESSING
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None


# ── Response schemas (what the API returns) ───────────────────────────────────

class TaskHistoryResponse(BaseModel):
    id: int
    task_id: int
    previous_status: Optional[str]
    current_status: str
    message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    task_type: TaskType
    priority: TaskPriority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class TaskDetailResponse(TaskResponse):
    """Extended response that includes the full history list."""
    history: List[TaskHistoryResponse] = []


class StatsResponse(BaseModel):
    total: int
    pending: int
    processing: int
    completed: int
    failed: int


class PaginatedTaskResponse(BaseModel):
    items: List[TaskResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
