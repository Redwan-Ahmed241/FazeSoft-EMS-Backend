"""
app/schemas/task.py — Pydantic schemas for Task.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    priority: TaskPriority = Field(default=TaskPriority.Medium)
    assigned_to: UUID
    deadline: date


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, min_length=1)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_to: Optional[UUID] = None
    deadline: Optional[date] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: UUID
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    project_id: UUID
    assigned_to: UUID
    assigned_by: UUID
    deadline: date
    created_at: datetime
    updated_at: datetime
