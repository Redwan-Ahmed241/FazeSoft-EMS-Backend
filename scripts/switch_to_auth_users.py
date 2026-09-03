"""
scripts/switch_to_auth_users.py — Point the app at Supabase's auth.users table.

1. Drops the removed public.users table (Supabase's auth.users is the source of truth).
2. Recreates user_role and project so their foreign keys target auth.users.id.

Run once:
    python -m scripts.switch_to_auth_users
"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import text

from app.core.database import engine, Base
import app.models  # noqa: F401


async def switch():
    print("[HireMate] Dropping public.users (Supabase auth.users is the source of truth)...")
    print("[HireMate] Rebuilding user_role / project against auth.users.id...")
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS public.users CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS public.user_role CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS public.project CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    print("[HireMate] Done. user_role and project now reference auth.users.id.")


if __name__ == "__main__":
    asyncio.run(switch())