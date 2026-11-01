"""Tests for robust URL normalization and handling for Amazon.in and Flipkart URLs."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_analyze_url_normalizes_missing_scheme_amazon(client: TestClient) -> None:
    """Missing https:// prefix on valid Amazon.in domain is automatically normalized."""
    resp = client.post(
        "/api/v1/harvester/analyze-url",
        json={"url": "www.amazon.in/dp/B0CS5X8P7B"},
        headers={"Authorization": "Bearer dev-bypass-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["canonical_url"] == "https://www.amazon.in/dp/B0CS5X8P7B"


def test_analyze_url_normalizes_missing_scheme_flipkart(client: TestClient) -> None:
    """Missing https:// prefix on valid Flipkart domain is automatically normalized."""
    resp = client.post(
        "/api/v1/harvester/analyze-url",
        json={"url": "www.flipkart.com/apple-iphone-15/p/itm123?pid=MOBGTAGPNRQA7CS3"},
        headers={"Authorization": "Bearer dev-bypass-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["asin"] == "MOBGTAGPNRQA7CS3"


def test_analyze_url_supports_uppercase_pid_flipkart(client: TestClient) -> None:
    """Flipkart URL with uppercase PID parameter name is accepted."""
    resp = client.post(
        "/api/v1/harvester/analyze-url",
        json={"url": "https://www.flipkart.com/p/itm123?PID=MOBGTAGPNRQA7CS3"},
        headers={"Authorization": "Bearer dev-bypass-token"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["asin"] == "MOBGTAGPNRQA7CS3"


def test_analyze_url_supports_m_flipkart_host(client: TestClient) -> None:
    """Mobile Flipkart hostname (m.flipkart.com) is supported."""
    resp = client.post(
        "/api/v1/harvester/analyze-url",
        json={"url": "https://m.flipkart.com/p/itm123?pid=MOBGTAGPNRQA7CS3"},
        headers={"Authorization": "Bearer dev-bypass-token"},
    )
    assert resp.status_code == 200


def test_analyze_url_still_rejects_insecure_http_scheme(client: TestClient) -> None:
    """Explicit http:// scheme is strictly rejected per security requirements."""
    resp = client.post(
        "/api/v1/harvester/analyze-url",
        json={"url": "http://www.amazon.in/dp/B0CS5X8P7B"},
        headers={"Authorization": "Bearer dev-bypass-token"},
    )
    assert resp.status_code == 422
