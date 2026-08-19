"""
app/schemas/notification.py — Pydantic schemas for Notification.
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class NotificationCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    type: str = "info"


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseModel):
    is_read: bool
