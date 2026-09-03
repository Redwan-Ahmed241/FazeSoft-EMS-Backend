"""
app/schemas/project.py — Pydantic schemas for Project.
"""
from datetime import datetime, date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    project_name: str
    project_code: str
    description: str
    client_id: UUID
    start_date: date
    end_date: date


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    project_code: Optional[str] = None
    description: Optional[str] = None
    client_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    project_name: str
    project_code: str
    description: str
    status: str
    manager_id: UUID
    client_id: UUID
    start_date: date
    end_date: date
    created_at: datetime
    updated_at: datetime


class ProjectListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: UUID
    project_name: str
    project_code: str
    status: str
    start_date: date
