"""Shared pytest fixtures. These tests do not require PostgreSQL."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(
        _env_file=None,
        app_name="reviewpulse-api",
        app_env="development",
        debug=False,
        cors_origins=["http://localhost:3000"],
        database_url=None,
        log_level="INFO",
    )


@pytest.fixture
def client(settings: Settings) -> Generator[TestClient]:
    get_settings.cache_clear()
    application = create_app(settings)
    application.dependency_overrides[get_settings] = lambda: settings
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    get_settings.cache_clear()
