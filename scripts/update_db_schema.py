"""
scripts/update_db_schema.py — Migration script for updating tables and RLS policies.

Run:
    python -m scripts.update_db_schema
"""
import sys
import os
import asyncio
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine


async def update_schema():
    print("Connecting to database and updating schema...")
    async with engine.begin() as conn:
        print("Updating profiles table columns...")
        await conn.execute(text("""
            ALTER TABLE public.profiles 
            ADD COLUMN IF NOT EXISTS phone text,
            ADD COLUMN IF NOT EXISTS location text,
            ADD COLUMN IF NOT EXISTS job_title text,
            ADD COLUMN IF NOT EXISTS bio text,
            ADD COLUMN IF NOT EXISTS avatar text;
        """))

        print("Updating users table columns...")
        await conn.execute(text("""
            ALTER TABLE public.users 
            ADD COLUMN IF NOT EXISTS role text NOT NULL DEFAULT 'candidate',
            ADD COLUMN IF NOT EXISTS phone text,
            ADD COLUMN IF NOT EXISTS location text,
            ADD COLUMN IF NOT EXISTS job_title text,
            ADD COLUMN IF NOT EXISTS bio text,
            ADD COLUMN IF NOT EXISTS avatar text;
        """))

        print("Updating candidates table columns...")
        await conn.execute(text("""
            ALTER TABLE public.candidates 
            ADD COLUMN IF NOT EXISTS education jsonb DEFAULT '[]',
            ADD COLUMN IF NOT EXISTS certifications jsonb DEFAULT '[]';
        """))

        print("Creating interviews table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.interviews (
                id SERIAL PRIMARY KEY,
                candidate_name text NOT NULL,
                candidate_email text NOT NULL,
                position text NOT NULL,
                date text NOT NULL,
                time text NOT NULL,
                duration text NOT NULL,
                type text NOT NULL,
                interviewer text NOT NULL,
                meeting_link text,
                avatar text,
                created_at timestamptz DEFAULT now()
            );
        """))

        print("Creating notifications table...")
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS public.notifications (
                id SERIAL PRIMARY KEY,
                user_id uuid NOT NULL,
                title text NOT NULL,
                message text NOT NULL,
                type text NOT NULL DEFAULT 'info',
                is_read boolean NOT NULL DEFAULT false,
                created_at timestamptz DEFAULT now()
            );
        """))

        print("Enabling RLS on interviews...")
        await conn.execute(text("ALTER TABLE public.interviews ENABLE ROW LEVEL SECURITY;"))

        await conn.execute(text("DROP POLICY IF EXISTS \"HR full access\" ON public.interviews;"))
        await conn.execute(text("DROP POLICY IF EXISTS \"Candidate reads own\" ON public.interviews;"))

        print("Creating policies on interviews...")
        await conn.execute(text("""
            CREATE POLICY "HR full access" ON public.interviews FOR ALL
            USING (public.get_my_role() = 'hr');
        """))
        await conn.execute(text("""
            CREATE POLICY "Candidate reads own" ON public.interviews FOR SELECT
            USING (
                candidate_email = (SELECT email FROM public.profiles WHERE id = auth.uid())
            );
        """))

        print("Enabling RLS on notifications...")
        await conn.execute(text("ALTER TABLE public.notifications ENABLE ROW LEVEL SECURITY;"))

        await conn.execute(text("DROP POLICY IF EXISTS \"Users read own\" ON public.notifications;"))
        await conn.execute(text("DROP POLICY IF EXISTS \"Users update own\" ON public.notifications;"))
        await conn.execute(text("DROP POLICY IF EXISTS \"HR write notifications\" ON public.notifications;"))

        print("Creating policies on notifications...")
        await conn.execute(text("""
            CREATE POLICY "Users read own" ON public.notifications FOR SELECT
            USING (user_id = auth.uid());
        """))
        await conn.execute(text("""
            CREATE POLICY "Users update own" ON public.notifications FOR UPDATE
            USING (user_id = auth.uid());
        """))
        await conn.execute(text("""
            CREATE POLICY "HR write notifications" ON public.notifications FOR INSERT
            WITH CHECK (true);
        """))

        print("Schema update completed successfully! ✅")


if __name__ == "__main__":
    asyncio.run(update_schema())
