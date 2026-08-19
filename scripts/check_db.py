"""
scripts/check_db.py — Check database schema columns.

Run:
    python -m scripts.check_db
"""
import sys
import os
import asyncio
from sqlalchemy import text

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine


async def check_db():
    print("Checking profiles columns...")
    async with engine.connect() as conn:
        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'profiles';
        """))
        columns = result.fetchall()
        print("Profiles columns:", columns)

        print("Altering profiles table if necessary...")
        await conn.execute(text("""
            ALTER TABLE public.profiles 
            ADD COLUMN IF NOT EXISTS phone text,
            ADD COLUMN IF NOT EXISTS location text,
            ADD COLUMN IF NOT EXISTS job_title text,
            ADD COLUMN IF NOT EXISTS bio text,
            ADD COLUMN IF NOT EXISTS avatar text;
        """))
        await conn.commit()
        print("Alter complete!")

        result = await conn.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'profiles';
        """))
        columns = result.fetchall()
        print("Profiles columns after alter:", columns)


if __name__ == "__main__":
    asyncio.run(check_db())
