"""
app/core/database.py — Async SQLAlchemy engine connected to PostgreSQL.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Safe fallback engine for import-time check/compilation (e.g. on Vercel builds)
if not DATABASE_URL:
    engine = create_async_engine(
        "postgresql+asyncpg://postgres:dummy@localhost:5432/postgres",
        echo=False,
    )
else:
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        connect_args={
            "prepared_statement_cache_size": 0,  # Required for Supabase pgBouncer pooler
        },
    )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an async DB session."""
    if not settings.DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not configured.")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
