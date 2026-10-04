"""
app/schemas/note.py — Pydantic schemas for Note.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

# Upper bound on stored note HTML, guarding against oversized payloads.
MAX_CONTENT_LENGTH = 200_000


class NoteCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=MAX_CONTENT_LENGTH)
    parent_id: Optional[UUID] = None
    order_index: Optional[int] = 0


class NoteUpdate(BaseModel):
    """Partial update — rename the note, save its content, or both."""
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    content: Optional[str] = Field(default=None, max_length=MAX_CONTENT_LENGTH)
    order_index: Optional[int] = None


class SubsectionOut(BaseModel):
    """Subsection view — concise item for sub-tabs."""
    model_config = ConfigDict(from_attributes=True)

    note_id: UUID
    parent_id: Optional[UUID] = None
    title: str
    order_index: int = 0
    created_at: datetime
    updated_at: datetime


class NoteListOut(BaseModel):
    """Tab-bar view — omits full content so listing stays cheap, includes subsections."""
    model_config = ConfigDict(from_attributes=True)

    note_id: UUID
    parent_id: Optional[UUID] = None
    title: str
    order_index: int = 0
    created_at: datetime
    updated_at: datetime
    subsections: List[SubsectionOut] = []


class NoteOut(NoteListOut):
    content: str
    subsections: List[SubsectionOut] = []


class SubsectionReorder(BaseModel):
    """Payload to update order_index for subsections."""
    order: List[UUID]


class SectionReorder(BaseModel):
    """Payload to update order_index for top-level sections."""
    order: List[UUID]

