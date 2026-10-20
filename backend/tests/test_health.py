"""Health, readiness, and routing tests. No live PostgreSQL required."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings
from app.main import create_app


def test_application_starts(client: TestClient) -> None:
    assert client.app is not None


def test_health_returns_expected_schema(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "reviewpulse-api"}


def test_ready_reports_unconfigured_database(client: TestClient) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["service"] == "reviewpulse-api"
    assert body["database"] == "unconfigured"


def test_ready_reports_unavailable_when_database_unreachable() -> None:
    settings = Settings(
        _env_file=None,
        app_name="reviewpulse-api",
        app_env="development",
        cors_origins=["http://localhost:3000"],
        database_url="postgresql://reviewpulse:reviewpulse@localhost:5432/reviewpulse",
    )
    get_settings.cache_clear()
    application = create_app(settings)
    application.dependency_overrides[get_settings] = lambda: settings
    with TestClient(application) as client:
        response = client.get("/api/v1/ready")
    application.dependency_overrides.clear()
    get_settings.cache_clear()

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["database"] == "unavailable"


def test_ready_reports_ok_when_database_connected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1 import health

    async def mock_check_db(_url: str) -> bool:
        return True

    monkeypatch.setattr(health, "check_database_connection", mock_check_db)

    settings = Settings(
        _env_file=None,
        app_name="reviewpulse-api",
        app_env="development",
        cors_origins=["http://localhost:3000"],
        database_url="postgresql://reviewpulse:reviewpulse@localhost:5432/reviewpulse",
    )
    get_settings.cache_clear()
    application = create_app(settings)
    application.dependency_overrides[get_settings] = lambda: settings
    with TestClient(application) as client:
        response = client.get("/api/v1/ready")
    application.dependency_overrides.clear()
    get_settings.cache_clear()

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"


def test_unknown_route_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    body = response.json()
    assert "detail" in body
    assert "Traceback" not in body["detail"]
    assert "traceback" not in str(body).lower()
