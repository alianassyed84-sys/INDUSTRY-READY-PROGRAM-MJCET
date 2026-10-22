"""Database engine, session management, and connectivity checks."""

import asyncio
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""


def get_async_database_url(url: str) -> str:
    """Ensure the database URL uses the asyncpg driver."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def get_engine(database_url: str, settings: Settings | None = None) -> AsyncEngine:
    """Return a cached or newly initialized AsyncEngine for the given URL."""
    global _engine, _sessionmaker
    async_url = get_async_database_url(database_url)
    resolved_settings = settings or get_settings()

    if _engine is None or str(_engine.url) != async_url:
        engine_kwargs: dict[str, object] = {
            "pool_pre_ping": resolved_settings.db_pool_pre_ping,
        }

        # PostgreSQL connection pool settings (avoid applying to SQLite)
        if not async_url.startswith("sqlite"):
            engine_kwargs.update(
                {
                    "pool_size": resolved_settings.db_pool_size,
                    "max_overflow": resolved_settings.db_max_overflow,
                    "pool_timeout": resolved_settings.db_pool_timeout,
                    "pool_recycle": resolved_settings.db_pool_recycle,
                }
            )

        _engine = create_async_engine(async_url, **engine_kwargs)
        _sessionmaker = async_sessionmaker(_engine, expire_on_commit=False)
    return _engine


def get_sessionmaker(
    database_url: str, settings: Settings | None = None
) -> async_sessionmaker[AsyncSession]:
    """Return a session factory for the given database URL."""
    get_engine(database_url, settings=settings)
    assert _sessionmaker is not None
    return _sessionmaker


async def close_database() -> None:
    """Dispose the cached database engine and reset session state."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _sessionmaker = None


async def get_db(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncIterator[AsyncSession | None]:
    """FastAPI dependency for yielding database sessions."""
    if not settings.database_url:
        yield None
        return
    session_factory = get_sessionmaker(settings.database_url)
    async with session_factory() as session:
        yield session


async def check_database_connection(
    database_url: str, timeout_seconds: float = 2.0
) -> bool:
    """Execute a lightweight SELECT 1 query to test database connectivity."""
    try:
        engine = get_engine(database_url)
        async with asyncio.timeout(timeout_seconds):
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
