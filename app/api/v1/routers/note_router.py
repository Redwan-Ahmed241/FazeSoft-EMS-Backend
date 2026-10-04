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
from app.schemas.note import NoteCreate, NoteListOut, NoteOut, NoteUpdate, SubsectionReorder, SectionReorder
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
    """Retrieve the logged-in user's top-level sections with their subsections."""
    return await NoteService.list_notes(db, current_user)


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=NoteOut, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_note(
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a section or subsection owned by the logged-in user."""
    return await NoteService.create_note(db, payload, current_user)


@router.post("/reorder", response_model=List[NoteListOut])
async def reorder_sections(
    payload: SectionReorder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reorder top-level sections."""
    return await NoteService.reorder_sections(db, payload.order, current_user)


@router.post("/{note_id}/divide", response_model=NoteOut)
async def divide_section(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Divide a section into subsections, migrating existing content to Subsection 1."""
    return await NoteService.divide_section(db, note_id, current_user)


@router.post("/{note_id}/subsections", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
async def create_subsection(
    note_id: UUID,
    payload: NoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a subsection under a section."""
    return await NoteService.create_subsection(db, note_id, payload, current_user)


@router.post("/{note_id}/subsections/reorder", response_model=NoteOut)
async def reorder_subsections(
    note_id: UUID,
    payload: SubsectionReorder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Reorder subsections of a section."""
    return await NoteService.reorder_subsections(db, note_id, payload.order, current_user)



@router.get("/{note_id}", response_model=NoteOut)
async def get_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve a single note or subsection belonging to the logged-in user."""
    return await NoteService.get_note(db, note_id, current_user)


@router.patch("/{note_id}", response_model=NoteOut)
async def update_note(
    note_id: UUID,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rename a note/subsection and/or save its content."""
    return await NoteService.update_note(db, note_id, payload, current_user)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a note or subsection belonging to the logged-in user."""
    await NoteService.delete_note(db, note_id, current_user)
