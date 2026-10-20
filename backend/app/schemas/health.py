"""Stable health and readiness response schemas."""

from typing import Literal

from pydantic import BaseModel

DatabaseCheck = Literal["ok", "unconfigured", "not_verified", "unavailable"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: str


class ReadyResponse(BaseModel):
    status: Literal["ok", "not_ready"]
    service: str
    database: DatabaseCheck
