"""
app/schemas/submission.py — Pydantic schemas for Task Submissions.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class SubmissionCreate(BaseModel):
    commit_link: Optional[str] = None
    notes: Optional[str] = None


class SubmissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    submission_id: UUID
    task_id: UUID
    submitted_by: UUID
    submitted_by_name: Optional[str] = None
    commit_link: Optional[str] = None
    notes: Optional[str] = None
    submitted_at: datetime
    created_at: datetime
