"""Shared pytest fixtures. These tests do not require PostgreSQL."""

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.auth import AuthenticatedUser, get_current_user, require_admin
from app.core.config import Settings, get_settings
from app.core.rate_limit import get_rate_limiter
from app.main import create_app

TEST_USER = AuthenticatedUser(
    user_id="test_user_id_123",
    email="testuser@example.com",
    roles=frozenset({"user"}),
    is_admin=False,
)

TEST_ADMIN_USER = AuthenticatedUser(
    user_id="test_admin_id_999",
    email="admin@example.com",
    roles=frozenset({"admin"}),
    is_admin=True,
)


@pytest.fixture(autouse=True)
def reset_rate_limiter() -> Generator[None]:
    """Ensure rate limiter state is reset for each test."""
    get_rate_limiter().reset()
    yield
    get_rate_limiter().reset()


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
    application.dependency_overrides[get_current_user] = lambda: TEST_USER
    application.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER
    with TestClient(application) as test_client:
        yield test_client
    application.dependency_overrides.clear()
    get_settings.cache_clear()
