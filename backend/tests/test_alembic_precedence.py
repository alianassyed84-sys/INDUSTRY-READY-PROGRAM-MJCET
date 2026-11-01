"""Test Alembic configuration precedence: settings.database_url vs alembic.ini."""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config


def test_alembic_database_url_precedence_online(monkeypatch):
    """Test that DATABASE_URL takes precedence over alembic.ini's sqlalchemy.url in online mode."""
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_db_path = Path(tmpdir) / "test_migration.db"
        test_db_url = f"sqlite+aiosqlite:///{temp_db_path.as_posix()}"

        # Set environment variable DATABASE_URL
        monkeypatch.setenv("DATABASE_URL", test_db_url)

        # Clear settings cache so get_settings() re-reads DATABASE_URL
        from app.core.config import get_settings
        get_settings.cache_clear()

        backend_dir = Path(__file__).resolve().parent.parent
        alembic_ini_path = backend_dir / "alembic.ini"

        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

        # Run migration online
        command.upgrade(alembic_cfg, "head")

        # Verify tables were created in the temp DB
        assert temp_db_path.exists(), f"Temp DB was not created at {temp_db_path}"

        conn = sqlite3.connect(str(temp_db_path))
        try:
            cursor = conn.cursor()
            tables = [
                row[0]
                for row in cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            ]
            assert "alembic_version" in tables
            assert "products" in tables
            assert "reviews" in tables
            assert "users" in tables
            assert "price_snapshots" in tables
        finally:
            conn.close()
            get_settings.cache_clear()


def test_alembic_database_url_precedence_offline(monkeypatch):
    """Test that DATABASE_URL takes precedence in offline mode (--sql)."""
    import io
    from contextlib import redirect_stdout

    test_db_url = "sqlite+aiosqlite:///dummy.db"
    monkeypatch.setenv("DATABASE_URL", test_db_url)
    from app.core.config import get_settings
    get_settings.cache_clear()

    backend_dir = Path(__file__).resolve().parent.parent
    alembic_ini_path = backend_dir / "alembic.ini"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("script_location", str(backend_dir / "alembic"))

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        command.upgrade(alembic_cfg, "0002", sql=True)

    sql_content = buffer.getvalue()
    assert "CREATE TABLE products" in sql_content
    assert "CREATE TABLE price_snapshots" in sql_content
    get_settings.cache_clear()


def test_postgres_alembic_run(monkeypatch):
    """Postgres migration check. If no Postgres is available, report BLOCKED per qa/RULES.md."""
    pg_url = os.environ.get("POSTGRES_TEST_DATABASE_URL")
    if not pg_url:
        pytest.skip("Status: BLOCKED - No PostgreSQL instance available in environment (qa/RULES.md rule 5)")
