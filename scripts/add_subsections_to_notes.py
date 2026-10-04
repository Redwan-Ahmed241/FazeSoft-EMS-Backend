"""
scripts/add_subsections_to_notes.py — Adds parent_id and order_index to notes table.

Idempotent: safe to run against an existing database.
"""
import sys
import os
import asyncio
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine


async def update_notes_schema():
    print("Checking and updating notes table schema...")
    async with engine.begin() as conn:
        await conn.execute(text("""
            ALTER TABLE public.notes
            ADD COLUMN IF NOT EXISTS parent_id uuid REFERENCES public.notes(note_id) ON DELETE CASCADE;
        """))

        await conn.execute(text("""
            ALTER TABLE public.notes
            ADD COLUMN IF NOT EXISTS order_index integer NOT NULL DEFAULT 0;
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_notes_parent_id ON public.notes (parent_id);
        """))

        res = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'notes'
            ORDER BY ordinal_position;
        """))
        columns = res.fetchall()
        print("Updated notes columns:", columns)

    print("notes table schema updated successfully.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(update_notes_schema())
