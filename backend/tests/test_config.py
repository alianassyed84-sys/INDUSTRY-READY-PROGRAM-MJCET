from pathlib import Path

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_production_requires_cors_origins() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, app_env="production", cors_origins=[])
    message = str(exc_info.value)
    assert "CORS_ORIGINS" in message
    assert "production" in message


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None, app_env="production", cors_origins=["*"])
    message = str(exc_info.value)
    assert "CORS_ORIGINS" in message
    assert "*" in message


def test_example_env_file_loads() -> None:
    env_example_path = Path(__file__).resolve().parent.parent / ".env.example"
    settings = Settings(_env_file=env_example_path)
    assert settings.app_env == "development"
    assert settings.database_url is None
    assert settings.cors_origins == ["http://localhost:3000"]


def test_cors_origins_accepts_comma_separated_string() -> None:
    settings = Settings(
        _env_file=None,
        cors_origins="http://localhost:3000,http://127.0.0.1:3000",
    )
    assert settings.cors_origins == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
