"""
app/api/v1/routers/note_router.py — Notepad CRUD endpoints, scoped to the logged-in user.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.note import NoteCreate, NoteListOut, NoteOut, NoteUpdate
from app.services.note_service import NoteService

router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=List[NoteListOut])
@router.get("/", response_model=List[NoteListOut], include_in_schema=False)
async def list_notes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the logged-in user's notes, most recently updated first."""
    return await NoteService.list_notes(db, current_user)


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a note owned by the logged-in user."""
    return await NoteService.create_note(db, payload, current_user)


@router.get("/{note_id}", response_model=NoteOut)
async def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a single note belonging to the logged-in user."""
    return await NoteService.get_note(db, note_id, current_user)


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rename a note and/or save its content."""
    return await NoteService.update_note(db, note_id, payload, current_user)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note belonging to the logged-in user."""
    await NoteService.delete_note(db, note_id, current_user)
