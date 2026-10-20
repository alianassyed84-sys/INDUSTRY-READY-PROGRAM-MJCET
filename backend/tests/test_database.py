"""Database configuration and connectivity unit tests."""

import pytest

from app.core.database import (
    Base,
    check_database_connection,
    close_database,
    get_async_database_url,
    get_engine,
    get_sessionmaker,
)


def test_get_async_database_url_converts_schemes() -> None:
    assert (
        get_async_database_url("postgresql://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert (
        get_async_database_url("postgres://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert (
        get_async_database_url("postgresql+asyncpg://user:pass@localhost:5432/db")
        == "postgresql+asyncpg://user:pass@localhost:5432/db"
    )
    assert (
        get_async_database_url("sqlite+aiosqlite:///:memory:")
        == "sqlite+aiosqlite:///:memory:"
    )


def test_base_metadata_is_available() -> None:
    assert Base.metadata is not None


def test_get_engine_and_sessionmaker() -> None:
    url = "postgresql://user:pass@localhost:5432/reviewpulse"
    engine = get_engine(url)
    assert engine is not None
    session_factory = get_sessionmaker(url)
    assert session_factory is not None


@pytest.mark.anyio
async def test_close_database_disposes_engine() -> None:
    url = "postgresql://user:pass@localhost:5432/reviewpulse"
    get_engine(url)
    await close_database()


@pytest.mark.anyio
async def test_check_database_connection_fails_gracefully_on_unreachable_host() -> None:
    # Port 59999 is typically unused and fails fast with connection refused
    url = "postgresql://invalid:invalid@127.0.0.1:59999/nonexistent"
    result = await check_database_connection(url, timeout_seconds=0.5)
    assert result is False
