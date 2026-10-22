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
    amazon_import_limit: int | None = 2500
    amazon_provider: str = "disabled"
    amazon_partner_tag: str | None = None
    amazon_access_key: str | None = None
    amazon_secret_key: str | None = None

    # Authentication & Authorization (Clerk JWT compatible)
    auth_enabled: bool = True
    clerk_issuer: str | None = None
    clerk_audience: str | None = None
    clerk_pem_public_key: str | None = None
    clerk_jwks_url: str | None = None
    clerk_secret_key: str | None = None

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_analysis: str = "60/minute"
    rate_limit_harvester: str = "10/minute"
    rate_limit_price_check: str = "20/minute"
    rate_limit_default: str = "120/minute"

    # Database Connection Pooling (PostgreSQL)
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: float = 30.0
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True

    @field_validator("db_pool_size")
    @classmethod
    def validate_pool_size(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("db_pool_size must be greater than 0.")
        return v

    @field_validator("db_max_overflow")
    @classmethod
    def validate_max_overflow(cls, v: int) -> int:
        if v < 0:
            raise ValueError("db_max_overflow must be non-negative.")
        return v

    @field_validator("db_pool_timeout")
    @classmethod
    def validate_pool_timeout(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("db_pool_timeout must be greater than 0.")
        return v

    @field_validator("db_pool_recycle")
    @classmethod
    def validate_pool_recycle(cls, v: int) -> int:
        if v < -1:
            raise ValueError("db_pool_recycle must be -1 or greater.")
        return v

    @field_validator(
        "database_url",
        "amazon_csv_path",
        "clerk_issuer",
        "clerk_audience",
        "clerk_pem_public_key",
        "clerk_jwks_url",
        "clerk_secret_key",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
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
