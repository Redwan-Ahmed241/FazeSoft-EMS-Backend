"""
app/schemas/note.py — Pydantic schemas for Note.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Upper bound on stored note HTML, guarding against oversized payloads.
MAX_CONTENT_LENGTH = 200_000


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=MAX_CONTENT_LENGTH)


class NoteUpdate(BaseModel):
    """Partial update — rename the note, save its content, or both."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, max_length=MAX_CONTENT_LENGTH)


class NoteListOut(BaseModel):
    """Tab-bar view — omits content so listing stays cheap."""
    model_config = ConfigDict(from_attributes=True)

    note_id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class NoteOut(NoteListOut):
    content: str
