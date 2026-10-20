"""Liveness and readiness endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.database import check_database_connection
from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter()

SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/health", response_model=HealthResponse)
def get_health(settings: SettingsDep) -> HealthResponse:
    """Return 200 when the application process is responsive."""
    return HealthResponse(status="ok", service=settings.app_name)


@router.get("/ready")
async def get_ready(settings: SettingsDep) -> JSONResponse:
    """Report dependency readiness with live database connectivity checking."""
    if settings.database_url is None:
        body = ReadyResponse(
            status="not_ready",
            service=settings.app_name,
            database="unconfigured",
        )
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=body.model_dump(),
        )

    is_healthy = await check_database_connection(settings.database_url)
    if is_healthy:
        body = ReadyResponse(
            status="ok",
            service=settings.app_name,
            database="ok",
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=body.model_dump(),
        )

    body = ReadyResponse(
        status="not_ready",
        service=settings.app_name,
        database="unavailable",
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=body.model_dump(),
    )
