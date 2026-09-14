"""
app/services/note_service.py — Business logic for the per-user Notepad.

Ownership is enforced inside every query: a note belonging to another user is
indistinguishable from a missing one (404), so note ids cannot be probed.
The owner is always taken from the authenticated user, never from the payload.
"""
from typing import List
from uuid import UUID as UUIDType

from fastapi import HTTPException, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.user import User
from app.schemas.note import NoteCreate, NoteUpdate


class NoteService:
    @staticmethod
    async def _get_owned_note(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> Note:
        result = await db.execute(
            select(Note).where(
                Note.note_id == note_id,
                Note.user_id == current_user.id,
            )
        )
        note = result.scalar_one_or_none()

        if not note:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id={note_id} not found.",
            )

        return note

    @staticmethod
    async def list_notes(db: AsyncSession, current_user: User) -> List[Note]:
        result = await db.execute(
            select(Note)
            .where(Note.user_id == current_user.id)
            .order_by(desc(Note.updated_at))
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_note(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> Note:
        return await NoteService._get_owned_note(db, note_id, current_user)

    @staticmethod
    async def create_note(
        db: AsyncSession, payload: NoteCreate, current_user: User
    ) -> Note:
        note = Note(
            user_id=current_user.id,
            title=payload.title.strip(),
            content=payload.content,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note

    @staticmethod
    async def update_note(
        db: AsyncSession, note_id: UUIDType, payload: NoteUpdate, current_user: User
    ) -> Note:
        note = await NoteService._get_owned_note(db, note_id, current_user)

        if payload.title is not None:
            note.title = payload.title.strip()
        if payload.content is not None:
            note.content = payload.content

        await db.commit()
        await db.refresh(note)
        return note

    @staticmethod
    async def delete_note(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> None:
        note = await NoteService._get_owned_note(db, note_id, current_user)
        await db.delete(note)
        await db.commit()
