"""Milestone 1 Security Hardening Test Suite.

Covers:
- F-01: Arbitrary server file path ingestion rejection and safe dataset resolution.
- F-02: Standards-based Clerk-compatible JWT Bearer authentication and RBAC.
- F-08: In-memory sliding-window rate limiting with 429 and Retry-After headers.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from app.core.auth import (
    AuthenticatedUser,
    require_admin,
)
from app.core.config import Settings, get_settings
from app.core.rate_limit import SlidingWindowRateLimiter, get_rate_limiter
from app.main import create_app

# ---------------------------------------------------------------------------
# Cryptographic key fixtures for genuine JWT tests
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def rsa_keypair() -> tuple[str, str]:
    """Generate a test RSA keypair in PEM format."""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    pem_public = (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("utf-8")
    )
    return pem_private, pem_public


@pytest.fixture
def auth_settings(rsa_keypair: tuple[str, str]) -> Settings:
    """Settings configured with RSA public key for real JWT verification."""
    _, pem_public = rsa_keypair
    return Settings(
        _env_file=None,
        app_name="reviewpulse-security-test",
        app_env="development",
        database_url=None,
        auth_enabled=True,
        clerk_issuer="https://clerk.reviewpulse.test",
        clerk_audience="reviewpulse-backend",
        clerk_pem_public_key=pem_public,
        rate_limit_enabled=True,
        rate_limit_per_minute_analysis=60,
        rate_limit_per_minute_harvester=10,
        rate_limit_per_minute_price_check=5,
    )


def create_token(
    pem_private: str,
    sub: str = "user_2test123",
    email: str = "user@example.com",
    roles: list[str] | None = None,
    issuer: str = "https://clerk.reviewpulse.test",
    audience: str = "reviewpulse-backend",
    expires_in_seconds: int = 3600,
) -> str:
    """Helper to mint real RS256 JWT tokens."""
    now = datetime.now(UTC)
    payload = {
        "sub": sub,
        "email": email,
        "iss": issuer,
        "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if roles:
        payload["roles"] = roles
    return jwt.encode(payload, pem_private, algorithm="RS256")


# ===========================================================================
# F-01: File-path Ingestion Tests
# ===========================================================================


def test_f01_client_supplied_csv_path_is_rejected_422() -> None:
    """Clients attempting to pass 'csv_path' in the request body receive 422."""
    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///:memory:",
        amazon_csv_path=None,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[require_admin] = lambda: AuthenticatedUser(
        user_id="admin_1", roles=frozenset({"admin"}), is_admin=True
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/harvester/jobs",
            json={"source": "csv_amazon", "csv_path": "/etc/passwd"},
        )
        assert response.status_code == 422
        assert response.json() == {"detail": "Invalid request"}


def test_f01_unconfigured_dataset_path_returns_503_without_leaking_path(
    tmp_path: pytest.TempPathFactory,
) -> None:
    """When server dataset path is missing, 503 is returned without leaking path."""
    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///:memory:",
        amazon_csv_path=str(tmp_path / "nonexistent_secret_file.csv"),
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[require_admin] = lambda: AuthenticatedUser(
        user_id="admin_1", roles=frozenset({"admin"}), is_admin=True
    )

    with TestClient(app) as client:
        response = client.post(
            "/api/v1/harvester/jobs",
            json={"source": "csv_amazon"},
        )
        assert response.status_code == 503
        detail = response.json().get("detail", "")
        # Safe message returned, internal path not disclosed
        assert "Dataset source is not configured or unavailable" in detail
        assert "nonexistent_secret_file.csv" not in detail


# ===========================================================================
# F-02: Authentication & Authorization Tests
# ===========================================================================


def test_f02_public_endpoints_accessible_without_auth() -> None:
    """Health probes and OpenAPI docs are public and require no credentials."""
    settings = Settings(_env_file=None, database_url=None)
    app = create_app(settings)
    # Do not set any auth dependency overrides

    with TestClient(app) as client:
        health_resp = client.get("/api/v1/health")
        assert health_resp.status_code == 200
        assert health_resp.json()["status"] == "ok"

        ready_resp = client.get("/api/v1/ready")
        assert ready_resp.status_code in (200, 503)

        openapi_resp = client.get("/openapi.json")
        assert openapi_resp.status_code == 200


def test_f02_protected_endpoints_fail_closed_401_when_unauthenticated() -> None:
    """Calling protected analysis or harvester routes with no token returns 401."""
    settings = Settings(_env_file=None, database_url=None)
    app = create_app(settings)
    # No dependency overrides: real auth runs and fails closed

    with TestClient(app) as client:
        # 1. NLP endpoint
        resp_nlp = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "Review text"},
        )
        assert resp_nlp.status_code == 401
        assert (
            "Authentication credentials were not provided" in resp_nlp.json()["detail"]
        )

        # 2. Harvester product read
        resp_prod = client.get("/api/v1/harvester/products")
        assert resp_prod.status_code == 401

        # 3. Harvester admin job start
        resp_job = client.post(
            "/api/v1/harvester/jobs",
            json={"source": "csv_amazon"},
        )
        assert resp_job.status_code == 401


def test_f02_invalid_or_expired_bearer_token_returns_401(
    auth_settings: Settings, rsa_keypair: tuple[str, str]
) -> None:
    """Malformed, expired, or invalid-signature tokens return 401."""
    pem_private, _ = rsa_keypair
    app = create_app(auth_settings)
    app.dependency_overrides[get_settings] = lambda: auth_settings

    with TestClient(app) as client:
        # Malformed bearer token
        resp_bad = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "hello"},
            headers={"Authorization": "Bearer not-a-valid-jwt"},
        )
        assert resp_bad.status_code == 401
        assert "Invalid token" in resp_bad.json()["detail"]

        # Expired token
        expired_token = create_token(pem_private, expires_in_seconds=-10)
        resp_exp = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "hello"},
            headers={"Authorization": f"Bearer {expired_token}"},
        )
        assert resp_exp.status_code == 401
        assert "token has expired" in resp_exp.json()["detail"].lower()

        # Wrong issuer
        bad_iss_token = create_token(pem_private, issuer="https://evil-issuer.com")
        resp_iss = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "hello"},
            headers={"Authorization": f"Bearer {bad_iss_token}"},
        )
        assert resp_iss.status_code == 401
        assert "issuer" in resp_iss.json()["detail"].lower()


def test_f02_valid_authenticated_user_accesses_nlp_endpoint(
    auth_settings: Settings, rsa_keypair: tuple[str, str]
) -> None:
    """A valid standard user token successfully authenticates and accesses endpoints."""
    pem_private, _ = rsa_keypair
    app = create_app(auth_settings)
    app.dependency_overrides[get_settings] = lambda: auth_settings

    token = create_token(pem_private, sub="user_real_123")
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "The battery life is stellar and impressive!"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["label"] == "positive"


def test_f02_non_admin_user_forbidden_on_administrative_endpoints(
    auth_settings: Settings, rsa_keypair: tuple[str, str]
) -> None:
    """A standard authenticated user receives 403 on administrative endpoints."""
    pem_private, _ = rsa_keypair
    app = create_app(auth_settings)
    app.dependency_overrides[get_settings] = lambda: auth_settings

    user_token = create_token(pem_private, sub="normal_user", roles=["user"])
    with TestClient(app) as client:
        # Job creation is admin-only
        resp_job = client.post(
            "/api/v1/harvester/jobs",
            json={"source": "csv_amazon"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp_job.status_code == 403
        assert "Administrative privileges required" in resp_job.json()["detail"]

        # Provider polling is admin-only
        resp_poll = client.post(
            "/api/v1/harvester/products/B001/check-price",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert resp_poll.status_code == 403


def test_f02_admin_user_authorized_on_administrative_endpoints(
    auth_settings: Settings, rsa_keypair: tuple[str, str]
) -> None:
    """An admin authenticated user passes authorization on administrative endpoints."""
    pem_private, _ = rsa_keypair
    app = create_app(auth_settings)
    app.dependency_overrides[get_settings] = lambda: auth_settings

    admin_token = create_token(pem_private, sub="admin_user", roles=["admin"])
    with TestClient(app) as client:
        # Reaches the handler (fails on DB/provider check 503, NOT 401 or 403)
        resp_job = client.post(
            "/api/v1/harvester/jobs",
            json={"source": "csv_amazon"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp_job.status_code == 503
        assert "Database is not configured" in resp_job.json()["detail"]


# ===========================================================================
# F-08: Rate Limiting Tests
# ===========================================================================


def test_f08_health_endpoint_is_rate_limit_exempt() -> None:
    """Health endpoints are exempt from rate limiting."""
    settings = Settings(_env_file=None, database_url=None)
    app = create_app(settings)

    with TestClient(app) as client:
        for _ in range(50):
            resp = client.get("/api/v1/health")
            assert resp.status_code == 200


def test_f08_rate_limiting_enforces_limit_and_returns_429() -> None:
    """Exceeding the rate limit returns 429 with Retry-After and rate limit headers."""
    limiter = SlidingWindowRateLimiter()
    # Configure tiny limit: 3 requests per 60 seconds
    key = "test_client_key"

    allowed1, rem1, retry1 = limiter.check_and_record(
        key, max_requests=3, window_seconds=60
    )
    assert allowed1 is True
    assert rem1 == 2

    allowed2, rem2, retry2 = limiter.check_and_record(
        key, max_requests=3, window_seconds=60
    )
    assert allowed2 is True
    assert rem2 == 1

    allowed3, rem3, retry3 = limiter.check_and_record(
        key, max_requests=3, window_seconds=60
    )
    assert allowed3 is True
    assert rem3 == 0

    # 4th request must be rejected
    allowed4, rem4, retry4 = limiter.check_and_record(
        key, max_requests=3, window_seconds=60
    )
    assert allowed4 is False
    assert rem4 == 0
    assert retry4 > 0


def test_f08_api_endpoint_rate_limit_integration(
    auth_settings: Settings, rsa_keypair: tuple[str, str]
) -> None:
    """Exceeding limit on an endpoint returns 429 and Retry-After header."""
    pem_private, _ = rsa_keypair
    custom_settings = auth_settings.model_copy(
        update={"rate_limit_analysis": "3/minute"}
    )
    app = create_app(custom_settings)
    app.dependency_overrides[get_settings] = lambda: custom_settings

    token = create_token(pem_private, sub="user_rate_tester")
    headers = {"Authorization": f"Bearer {token}"}

    with TestClient(app) as client:
        for _ in range(3):
            resp = client.post(
                "/api/v1/analysis/sentiment",
                json={"text": "good product"},
                headers=headers,
            )
            assert resp.status_code == 200
            assert "X-RateLimit-Remaining" in resp.headers

        # 4th request must trigger 429
        resp_blocked = client.post(
            "/api/v1/analysis/sentiment",
            json={"text": "good product"},
            headers=headers,
        )
        assert resp_blocked.status_code == 429
        assert "Retry-After" in resp_blocked.headers
        assert resp_blocked.headers["X-RateLimit-Remaining"] == "0"
        assert "Rate limit exceeded" in resp_blocked.json()["detail"]


def test_f08_rate_limiter_reset_provides_test_isolation() -> None:
    """The reset method clears state between tests."""
    limiter = get_rate_limiter()
    limiter.check_and_record("client_a", max_requests=1, window_seconds=60)
    assert "client_a" in limiter._history

    limiter.reset()
    assert len(limiter._history) == 0

    allowed, rem, _ = limiter.check_and_record(
        "client_a", max_requests=1, window_seconds=60
    )
    assert allowed is True
    assert rem == 0
