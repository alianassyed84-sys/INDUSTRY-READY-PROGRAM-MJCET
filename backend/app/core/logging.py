"""Structured process logging and request correlation tracing."""

from __future__ import annotations

import contextvars
import logging
import re
import sys
import time
import uuid
from typing import TYPE_CHECKING

from starlette.types import ASGIApp, Message, Receive, Scope, Send

if TYPE_CHECKING:
    from app.core.config import Settings

# Context variables for asynchronous request correlation
request_id_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
request_path_ctx: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "request_path", default=None
)

# Request ID validation policy constants
_MAX_REQUEST_ID_LEN = 128
_REQUEST_ID_RE = re.compile(r"^[a-zA-Z0-9_\-\.:]{1,128}$")


def is_valid_request_id(value: str | None) -> bool:
    """Validate incoming request ID format, character set, and length.

    Validation policy:
    - Must be a non-empty string between 1 and 128 characters.
    - Restricted to safe characters: alphanumeric, hyphen, underscore, period, colon.
    - Explicitly rejects control characters, CRLF injection, null bytes, and non-ASCII.
    """
    if not value or not isinstance(value, str):
        return False
    trimmed = value.strip()
    if not trimmed or len(trimmed) > _MAX_REQUEST_ID_LEN:
        return False
    return bool(_REQUEST_ID_RE.match(trimmed))


def generate_request_id() -> str:
    """Generate an unpredictable, cryptographically random UUID4 request identifier."""
    return str(uuid.uuid4())


def resolve_request_id(incoming: str | None) -> str:
    """Return validated incoming request ID or generate a fresh UUID4."""
    if is_valid_request_id(incoming):
        assert incoming is not None
        return incoming.strip()
    return generate_request_id()


def get_request_id() -> str | None:
    """Return the active correlation request ID from context, if available."""
    return request_id_ctx.get()


class StructuredFormatter(logging.Formatter):
    """Emit compact key=value log lines suitable for local development."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S")
        parts = [
            f"ts={timestamp}",
            f"level={record.levelname}",
            f"logger={record.name}",
            f"msg={record.getMessage()}",
        ]
        request_id = getattr(record, "request_id", None)
        path = getattr(record, "path", None)
        if request_id:
            parts.append(f"request_id={request_id}")
        if path:
            parts.append(f"path={path}")
        if record.exc_info:
            parts.append("exc=1")
        return " ".join(parts)


class CorrelationFilter(logging.Filter):
    """Logging filter that injects contextual request_id and path into LogRecord."""

    def filter(self, record: logging.LogRecord) -> bool:
        if getattr(record, "request_id", None) is None:
            record.request_id = request_id_ctx.get()
        if getattr(record, "path", None) is None:
            record.path = request_path_ctx.get()
        return True


class RequestIdMiddleware:
    """Pure ASGI middleware for request correlation tracing and structured logs.

    1. Extracts incoming X-Request-ID, validates safety, or generates a UUID4.
    2. Injects request_id into ContextVar and scope['state']['request_id'].
    3. Guarantees X-Request-ID header in every outgoing HTTP response.
    4. Emits structured completion logs without leaking sensitive headers/bodies.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        raw_header: str | None = None
        for name, value in scope.get("headers", []):
            if name.lower() == b"x-request-id":
                try:
                    raw_header = value.decode("latin-1")
                except Exception:
                    raw_header = None
                break

        request_id = resolve_request_id(raw_header)
        path = scope.get("path", "")
        method = scope.get("method", "")

        # Set context variables for logging and downstream processing
        id_token = request_id_ctx.set(request_id)
        path_token = request_path_ctx.set(path)

        # Populate request.state.request_id in ASGI scope
        if "state" not in scope:
            scope["state"] = {}
        scope["state"]["request_id"] = request_id

        start_time = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
                headers_list = [
                    h
                    for h in message.get("headers", [])
                    if h[0].lower() != b"x-request-id"
                ]
                headers_list.append((b"x-request-id", request_id.encode("latin-1")))
                message["headers"] = headers_list
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger = logging.getLogger("app.request")
            logger.info(
                "request completed method=%s status=%d duration_ms=%.2f",
                method,
                status_code,
                duration_ms,
            )
            request_id_ctx.reset(id_token)
            request_path_ctx.reset(path_token)


def configure_logging(settings: Settings) -> None:
    """Configure the root logger once for the process."""
    level_name = settings.log_level.upper()
    level = getattr(logging, level_name, logging.INFO)
    corr_filter = CorrelationFilter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    handler.addFilter(corr_filter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.addFilter(corr_filter)
    root.setLevel(level)
