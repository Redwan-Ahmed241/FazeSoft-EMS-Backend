"""
scripts/migrate.py — Creates all database tables in PostgreSQL.
Run once after setting up your .env file:
    python -m scripts.migrate
"""
import sys
import os
import asyncio

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.database import engine, Base
import app.models  # noqa: F401


async def create_tables():
    print("[HireMate] Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[HireMate] Tables created successfully!")


if __name__ == "__main__":
    asyncio.run(create_tables())
