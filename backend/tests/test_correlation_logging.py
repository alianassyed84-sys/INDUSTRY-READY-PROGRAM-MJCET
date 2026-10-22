"""Tests for request correlation IDs and structured request logging (F-09).

Covers:
- Acceptance of valid incoming X-Request-ID headers.
- Rejection of invalid, oversized, or control-character/CRLF-injected headers.
- Generation of unpredictable UUID4 request IDs when missing or invalid.
- Consistent presence of X-Request-ID on all responses (200, 401, 404, 422, 500).
- Availability of request_id in request.state and contextvars.
- Log correlation in structured log records.
- Prevention of sensitive header/payload logging in request logs.
"""

from __future__ import annotations

import logging
import re
import uuid
from typing import Any

import pytest
from fastapi import APIRouter, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.core.config import Settings
from app.core.logging import (
    StructuredFormatter,
    generate_request_id,
    get_request_id,
    is_valid_request_id,
    resolve_request_id,
)
from app.main import create_app

_UUID_REGEX = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


@pytest.fixture
def test_app():
    """Create a configured test application instance with debug endpoints."""
    settings = Settings(
        _env_file=None,
        app_name="reviewpulse-log-test",
        app_env="development",
        database_url=None,
        auth_enabled=False,
    )
    app = create_app(settings)

    # Attach diagnostic test endpoints to verify internal state and exceptions
    test_router = APIRouter(prefix="/test-diagnostics")

    class SampleModel(BaseModel):
        name: str
        count: int

    @test_router.get("/echo-id")
    def echo_id() -> dict[str, Any]:
        return {"context_request_id": get_request_id()}

    @test_router.post("/validate-body")
    def validate_body(payload: SampleModel) -> dict[str, Any]:
        return {"name": payload.name, "count": payload.count}

    @test_router.get("/trigger-unhandled")
    def trigger_unhandled() -> None:
        raise RuntimeError("Simulated crash for 500 test")

    @test_router.get("/trigger-http-error")
    def trigger_http_error() -> None:
        raise HTTPException(status_code=403, detail="Forbidden access")

    app.include_router(test_router)
    return app


# ===========================================================================
# 1. Validation Policy Unit Tests
# ===========================================================================


def test_validation_policy_valid_ids() -> None:
    """Standard alphanumeric, UUID, hyphenated, dot, and colon IDs are accepted."""
    assert is_valid_request_id("req-12345") is True
    assert is_valid_request_id("user_test.1:abc-XYZ") is True
    assert is_valid_request_id(str(uuid.uuid4())) is True
    assert is_valid_request_id("A" * 128) is True


def test_validation_policy_invalid_ids() -> None:
    """Invalid, oversized, or control-character/CRLF-injected IDs are rejected."""
    assert is_valid_request_id(None) is False
    assert is_valid_request_id("") is False
    assert is_valid_request_id("   ") is False
    assert is_valid_request_id("A" * 129) is False  # exceeds 128 chars
    assert is_valid_request_id("req\r\nInjected: True") is False  # CRLF injection
    assert is_valid_request_id("req\nid") is False  # newline
    assert is_valid_request_id("req\x00id") is False  # null byte
    assert is_valid_request_id("req with spaces") is False
    assert is_valid_request_id("req<script>") is False
    assert is_valid_request_id("req;DROP TABLE") is False


def test_resolve_request_id_returns_clean_or_generates() -> None:
    """resolve_request_id preserves valid inputs and generates UUID4 for invalid."""
    assert resolve_request_id("valid-id-001") == "valid-id-001"
    assert resolve_request_id("  valid-with-spaces  ") == "valid-with-spaces"

    generated = resolve_request_id("bad\r\ninjection")
    assert _UUID_REGEX.match(generated) is not None

    generated_none = resolve_request_id(None)
    assert _UUID_REGEX.match(generated_none) is not None


def test_generate_request_id_is_unpredictable() -> None:
    """Successive generated request IDs are distinct valid UUID4 strings."""
    id1 = generate_request_id()
    id2 = generate_request_id()
    assert id1 != id2
    assert _UUID_REGEX.match(id1) is not None
    assert _UUID_REGEX.match(id2) is not None


# ===========================================================================
# 2. Response Header & Propagation Tests
# ===========================================================================


def test_generated_request_id_when_missing(test_app) -> None:
    """When client provides no X-Request-ID, server generates and returns a UUID4."""
    with TestClient(test_app) as client:
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        req_id = resp.headers.get("x-request-id")
        assert req_id is not None
        assert _UUID_REGEX.match(req_id) is not None


def test_valid_incoming_request_id_preserved(test_app) -> None:
    """A valid client-supplied X-Request-ID is preserved and echoed on response."""
    custom_id = "trace-client-12345.abc_XYZ"
    with TestClient(test_app) as client:
        resp = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
        assert resp.status_code == 200
        assert resp.headers.get("x-request-id") == custom_id


@pytest.mark.parametrize(
    "invalid_header",
    [
        "injected\r\nX-Bad: evil",
        "injected\nBad",
        "null\x00byte",
        "a" * 129,
        "bad spaces in id",
        "bad<tag>",
        "bad;command",
    ],
)
def test_invalid_incoming_request_id_rejected_and_replaced(
    test_app, invalid_header: str
) -> None:
    """Unsafe or invalid X-Request-ID headers are replaced by unpredictable UUID4."""
    with TestClient(test_app) as client:
        resp = client.get("/api/v1/health", headers={"X-Request-ID": invalid_header})
        assert resp.status_code == 200
        req_id = resp.headers.get("x-request-id")
        assert req_id is not None
        assert req_id != invalid_header
        assert _UUID_REGEX.match(req_id) is not None
        assert "\r" not in req_id
        assert "\n" not in req_id


def test_context_and_state_contain_request_id(test_app) -> None:
    """get_request_id() returns the current active ID during route execution."""
    custom_id = "trace-diag-test-999"
    with TestClient(test_app) as client:
        resp = client.get(
            "/test-diagnostics/echo-id", headers={"X-Request-ID": custom_id}
        )
        assert resp.status_code == 200
        assert resp.headers.get("x-request-id") == custom_id
        assert resp.json() == {"context_request_id": custom_id}


# ===========================================================================
# 3. Error Responses & Exception Propagation
# ===========================================================================


def test_request_id_on_http_exceptions(test_app) -> None:
    """HTTP 403 and 404 responses include the X-Request-ID header."""
    with TestClient(test_app) as client:
        resp_403 = client.get(
            "/test-diagnostics/trigger-http-error",
            headers={"X-Request-ID": "err-test-403"},
        )
        assert resp_403.status_code == 403
        assert resp_403.headers.get("x-request-id") == "err-test-403"

        resp_404 = client.get(
            "/non-existent-path-987",
            headers={"X-Request-ID": "err-test-404"},
        )
        assert resp_404.status_code == 404
        assert resp_404.headers.get("x-request-id") == "err-test-404"


def test_request_id_on_validation_errors(test_app) -> None:
    """HTTP 422 validation errors include the X-Request-ID header."""
    with TestClient(test_app) as client:
        resp_422 = client.post(
            "/test-diagnostics/validate-body",
            json={"bad_field": 123},
            headers={"X-Request-ID": "err-test-422"},
        )
        assert resp_422.status_code == 422
        assert resp_422.headers.get("x-request-id") == "err-test-422"


def test_request_id_on_unhandled_exception(test_app) -> None:
    """Unhandled exceptions (HTTP 500) include X-Request-ID on the response."""
    with TestClient(test_app, raise_server_exceptions=False) as client:
        resp_500 = client.get(
            "/test-diagnostics/trigger-unhandled",
            headers={"X-Request-ID": "crash-test-500"},
        )
        assert resp_500.status_code == 500
        assert resp_500.headers.get("x-request-id") == "crash-test-500"
        assert resp_500.json() == {"detail": "Internal server error"}


# ===========================================================================
# 4. Structured Logging & Sensitive Data Redaction
# ===========================================================================


def test_log_records_contain_request_id(test_app, caplog) -> None:
    """Application logs emitted during a request have request_id set via filter."""
    caplog.set_level(logging.INFO)
    req_id = "test-log-record-id-101"

    with TestClient(test_app) as client:
        resp = client.get("/api/v1/health", headers={"X-Request-ID": req_id})
        assert resp.status_code == 200

    # Locate completion log emitted by RequestIdMiddleware
    req_logs = [r for r in caplog.records if r.name == "app.request"]
    assert len(req_logs) >= 1
    completion_record = req_logs[0]
    assert getattr(completion_record, "request_id", None) == req_id
    assert "status=200" in completion_record.getMessage()
    assert "duration_ms=" in completion_record.getMessage()


def test_structured_formatter_includes_request_id() -> None:
    """StructuredFormatter formats record with request_id= and path= attributes."""
    formatter = StructuredFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Sample event",
        args=(),
        exc_info=None,
    )
    record.request_id = "test-fmt-id-555"
    record.path = "/api/v1/test"

    formatted = formatter.format(record)
    assert "request_id=test-fmt-id-555" in formatted
    assert "path=/api/v1/test" in formatted
    assert "level=INFO" in formatted
    assert "msg=Sample event" in formatted


def test_no_sensitive_headers_or_bodies_in_request_logs(test_app, caplog) -> None:
    """Request logs do not leak Authorization tokens, passwords, cookies, or bodies."""
    caplog.set_level(logging.INFO)

    secret_jwt = "secret_eyJh.eyJzdWIiOiIxMjMifQ.signature"
    secret_cookie = "secret_session_token_xyz"
    secret_body_content = "super_secret_password_abc"

    with TestClient(test_app) as client:
        client.post(
            "/api/v1/analysis/sentiment",
            headers={
                "Authorization": f"Bearer {secret_jwt}",
                "Cookie": f"session={secret_cookie}",
                "X-Request-ID": "safe-id-007",
            },
            json={
                "text": "Great product!",
                "password": secret_body_content,
            },
        )

    # Search all captured log output
    full_log_text = " ".join(record.getMessage() for record in caplog.records)

    assert secret_jwt not in full_log_text
    assert secret_cookie not in full_log_text
    assert secret_body_content not in full_log_text
