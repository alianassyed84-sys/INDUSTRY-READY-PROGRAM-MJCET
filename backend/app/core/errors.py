"""HTTP error responses that do not leak internal exception details."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that return a stable, non-sensitive JSON body."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return JSONResponse(status_code=exc.status_code, content={"detail": detail})

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        logger.info("Invalid request path=%s", request.url.path)
        return JSONResponse(status_code=422, content={"detail": "Invalid request"})

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
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
