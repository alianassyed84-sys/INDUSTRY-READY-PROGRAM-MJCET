"""Environment-based application settings."""

import json
from functools import lru_cache
from typing import Annotated, Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

AppEnv = Literal["development", "staging", "production"]


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and an optional .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_ignore_empty=True,
    )

    app_name: str = "reviewpulse-api"
    app_env: AppEnv = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    database_url: str | None = None
    log_level: str = "INFO"
    amazon_csv_path: str | None = None
    amazon_provider: str = "disabled"
    amazon_partner_tag: str | None = None
    amazon_access_key: str | None = None
    amazon_secret_key: str | None = None

    @field_validator("database_url", mode="before")
    @classmethod
    def empty_database_url_to_none(cls, value: object) -> object:
        if isinstance(value, str) and value.strip() == "":
            return None
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if value is None:
            return []
        if isinstance(value, str):
            stripped = value.strip()
            if stripped == "":
                return []
            if stripped.startswith("["):
                parsed = json.loads(stripped)
                if not isinstance(parsed, list):
                    raise ValueError(
                        "CORS_ORIGINS JSON value must be a list of origins"
                    )
                return parsed
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value

    @model_validator(mode="after")
    def validate_production_cors(self) -> Self:
        if self.app_env != "production":
            return self
        if not self.cors_origins:
            raise ValueError(
                "CORS_ORIGINS must be a non-empty list when APP_ENV is production"
            )
        if "*" in self.cors_origins:
            raise ValueError(
                "CORS_ORIGINS must not include '*' when APP_ENV is production"
            )
        return self


@lru_cache
def get_settings() -> Settings:
    """Return cached settings. Call cache_clear() in tests after env changes."""
    return Settings()
