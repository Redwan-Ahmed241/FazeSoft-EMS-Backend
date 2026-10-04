"""
app/services/note_service.py — Business logic for the per-user Notepad.

Ownership is enforced inside every query: a note belonging to another user is
indistinguishable from a missing one (404), so note ids cannot be probed.
The owner is always taken from the authenticated user, never from the payload.
"""
from typing import List
from uuid import UUID as UUIDType

from fastapi import HTTPException, status
from sqlalchemy import select, desc, update, func
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

        # Explicitly fetch child subsections to avoid lazy-loading concurrency traps
        subs_res = await db.execute(
            select(Note)
            .where(
                Note.parent_id == note_id,
                Note.user_id == current_user.id,
            )
            .order_by(Note.order_index, Note.created_at)
        )
        note.subsections = list(subs_res.scalars().all())
        return note

    @staticmethod
    async def list_notes(db: AsyncSession, current_user: User) -> List[Note]:
        """List all top-level sections (where parent_id is NULL) for the user, with subsections attached."""
        result = await db.execute(
            select(Note)
            .where(
                Note.user_id == current_user.id,
                Note.parent_id.is_(None),
            )
            .order_by(Note.order_index, Note.created_at)
        )
        sections = list(result.scalars().all())

        if not sections:
            return []

        section_ids = [s.note_id for s in sections]
        subs_result = await db.execute(
            select(Note)
            .where(
                Note.user_id == current_user.id,
                Note.parent_id.in_(section_ids),
            )
            .order_by(Note.order_index, Note.created_at)
        )
        all_subs = list(subs_result.scalars().all())

        subs_by_parent = {}
        for sub in all_subs:
            subs_by_parent.setdefault(sub.parent_id, []).append(sub)

        for s in sections:
            s.subsections = subs_by_parent.get(s.note_id, [])

        return sections

    @staticmethod
    async def get_note(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> Note:
        return await NoteService._get_owned_note(db, note_id, current_user)

    @staticmethod
    async def create_note(
        db: AsyncSession, payload: NoteCreate, current_user: User
    ) -> Note:
        if payload.parent_id:
            # Verify the parent note exists and belongs to the user
            await NoteService._get_owned_note(db, payload.parent_id, current_user)
            order_index = payload.order_index or 0
        else:
            if payload.order_index is None or payload.order_index == 0:
                count_res = await db.execute(
                    select(func.count())
                    .select_from(Note)
                    .where(Note.user_id == current_user.id, Note.parent_id.is_(None))
                )
                order_index = count_res.scalar() or 0
            else:
                order_index = payload.order_index

        note = Note(
            user_id=current_user.id,
            parent_id=payload.parent_id,
            order_index=order_index,
            title=payload.title.strip(),
            content=payload.content,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        note.subsections = []
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
        if payload.order_index is not None:
            note.order_index = payload.order_index

        await db.commit()
        await db.refresh(note)
        return await NoteService._get_owned_note(db, note_id, current_user)

    @staticmethod
    async def delete_note(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> None:
        note = await NoteService._get_owned_note(db, note_id, current_user)
        await db.delete(note)
        await db.commit()

    @staticmethod
    async def divide_section(
        db: AsyncSession, note_id: UUIDType, current_user: User
    ) -> Note:
        """Divide a section into subsections, migrating existing content to Subsection 1."""
        section = await NoteService._get_owned_note(db, note_id, current_user)

        # If already divided into subsections, return as-is
        if section.subsections and len(section.subsections) > 0:
            return section

        sub1 = Note(
            user_id=current_user.id,
            parent_id=note_id,
            title="Subsection 1",
            content=section.content,
            order_index=0,
        )
        sub2 = Note(
            user_id=current_user.id,
            parent_id=note_id,
            title="Subsection 2",
            content="",
            order_index=1,
        )
        db.add(sub1)
        db.add(sub2)
        section.content = ""
        await db.commit()

        return await NoteService._get_owned_note(db, note_id, current_user)

    @staticmethod
    async def create_subsection(
        db: AsyncSession, parent_id: UUIDType, payload: NoteCreate, current_user: User
    ) -> Note:
        """Create a new subsection under the specified parent section."""
        parent = await NoteService._get_owned_note(db, parent_id, current_user)
        next_order = len(parent.subsections) if parent.subsections else 0

        sub = Note(
            user_id=current_user.id,
            parent_id=parent_id,
            title=payload.title.strip(),
            content=payload.content or "",
            order_index=next_order,
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)
        sub.subsections = []
        return sub

    @staticmethod
    async def reorder_subsections(
        db: AsyncSession, parent_id: UUIDType, order_ids: List[UUIDType], current_user: User
    ) -> Note:
        """Update order_index for subsections under a parent section."""
        parent = await NoteService._get_owned_note(db, parent_id, current_user)

        for idx, sub_id in enumerate(order_ids):
            await db.execute(
                update(Note)
                .where(
                    Note.note_id == sub_id,
                    Note.parent_id == parent_id,
                    Note.user_id == current_user.id,
                )
                .values(order_index=idx)
            )

        await db.commit()
        return await NoteService._get_owned_note(db, parent_id, current_user)

    @staticmethod
    async def reorder_sections(
        db: AsyncSession, order_ids: List[UUIDType], current_user: User
    ) -> List[Note]:
        """Update order_index for top-level sections."""
        for idx, note_id in enumerate(order_ids):
            await db.execute(
                update(Note)
                .where(
                    Note.note_id == note_id,
                    Note.parent_id.is_(None),
                    Note.user_id == current_user.id,
                )
                .values(order_index=idx)
            )

        await db.commit()
        return await NoteService.list_notes(db, current_user)

