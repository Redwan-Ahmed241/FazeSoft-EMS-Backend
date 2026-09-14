"""
scripts/setup_candidate_trigger.py — Create Postgres trigger on auth.users to auto-assign Candidate role in user_role.
"""
import sys
import os
import asyncio
from sqlalchemy import text

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.core.database import engine

SQL_FUNC = """
CREATE OR REPLACE FUNCTION public.handle_new_user_role()
RETURNS TRIGGER AS $$
DECLARE
    v_role_id uuid;
BEGIN
    SELECT id INTO v_role_id 
    FROM public.role 
    WHERE role_desc ILIKE 'Candidate' OR name ILIKE 'Candidate' 
    LIMIT 1;

    IF v_role_id IS NOT NULL THEN
        INSERT INTO public.user_role (user_id, role_id)
        VALUES (NEW.id, v_role_id)
        ON CONFLICT (user_id, role_id) DO NOTHING;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""

SQL_DROP = "DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;"

SQL_TRIGGER = """
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user_role();
"""

async def apply():
    print("Setting up Candidate trigger on auth.users...")
    async with engine.begin() as conn:
        await conn.execute(text(SQL_FUNC))
        await conn.execute(text(SQL_DROP))
        await conn.execute(text(SQL_TRIGGER))
    print("Trigger created successfully!")

if __name__ == "__main__":
    asyncio.run(apply())
