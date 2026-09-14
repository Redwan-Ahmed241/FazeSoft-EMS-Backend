"""
scripts/create_notes_table.py — Creates the notes table for the Notepad feature.

Idempotent: safe to run against an existing database.

Run:
    python -m scripts.create_notes_table
"""
import sys
import os
import asyncio
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine


async def create_notes_table():
    print("Connecting to database and creating notes table...")
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.notes (
                note_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
                title varchar(255) NOT NULL,
                content text NOT NULL DEFAULT '',
                created_at timestamptz NOT NULL DEFAULT now(),
                updated_at timestamptz NOT NULL DEFAULT now()
            );
        """))

        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_notes_user_id ON public.notes (user_id);
        """))

    print("notes table is ready.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_notes_table())
