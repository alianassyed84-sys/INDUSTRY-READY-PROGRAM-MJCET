"""HTTP error responses that do not leak internal exception details."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_request_id

logger = logging.getLogger(__name__)


def _get_correlation_headers(
    request: Request, existing_headers: dict[str, str] | None = None
) -> dict[str, str]:
    headers = dict(existing_headers or {})
    req_id = getattr(request.state, "request_id", None) or get_request_id()
    if req_id and "X-Request-ID" not in headers:
        headers["X-Request-ID"] = req_id
    return headers


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers returning stable JSON responses with correlation headers."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        headers = _get_correlation_headers(request, exc.headers)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": detail},
            headers=headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info("Invalid request path=%s", request.url.path)
        headers = _get_correlation_headers(request)
        return JSONResponse(
            status_code=422,
            content={"detail": "Invalid request"},
            headers=headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        _exc: Exception,
    ) -> JSONResponse:
        logger.exception(
            "Unhandled error method=%s path=%s",
            request.method,
            request.url.path,
        )
        headers = _get_correlation_headers(request)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
            headers=headers,
        )
