"""API-level integration tests for Flipkart reviews scraper endpoints:
- POST /api/v1/harvester/flipkart/scrape
- POST /api/v1/harvester/analyze-url with Flipkart URLs
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import get_current_user, require_admin
from app.core.config import Settings, get_settings
from app.core.database import Base, get_db
from app.main import create_app
from app.models.product import Product
from app.models.review import Review
from tests.conftest import TEST_ADMIN_USER, TEST_USER


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.anyio
async def test_scrape_flipkart_success(async_session: AsyncSession) -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        app_env="development",
        auth_enabled=False,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: async_session
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

    with TestClient(app) as client:
        url = (
            "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
            "?pid=MOBGTAGPNRQA7CS3"
        )
        resp = client.post(
            "/api/v1/harvester/flipkart/scrape",
            json={"url": url, "max_items": 4, "max_pages_per_product": 2},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["product_id"] == "MOBGTAGPNRQA7CS3"
        assert "Apple Iphone 15" in data["product_name"]
        assert data["reviews_count"] == 4
        assert len(data["reviews"]) == 4
        assert data["estimated_cost_usd"] > 0
        assert data["product"]["product_id"] == "MOBGTAGPNRQA7CS3"

        # Verify review details
        for rev in data["reviews"]:
            assert rev["productId"] == "MOBGTAGPNRQA7CS3"
            assert rev["reviewId"] != ""
            assert rev["rating"] is not None
            assert rev["text"] is not None

        # Check NLP insights returned
        assert data["insights"] is not None
        assert data["insights"]["total_reviews_analyzed"] == 4

        # Verify database persistence
        db_prod = (
            await async_session.execute(
                select(Product).where(Product.product_id == "MOBGTAGPNRQA7CS3")
            )
        ).scalar_one_or_none()
        assert db_prod is not None

        db_reviews = (
            (
                await async_session.execute(
                    select(Review).where(Review.product_id == "MOBGTAGPNRQA7CS3")
                )
            )
            .scalars()
            .all()
        )
        assert len(db_reviews) == 4

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_scrape_flipkart_rejects_invalid_url(async_session: AsyncSession) -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        app_env="development",
        auth_enabled=False,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: async_session
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

    with TestClient(app) as client:
        # Missing pid parameter
        resp = client.post(
            "/api/v1/harvester/flipkart/scrape",
            json={"url": "https://www.flipkart.com/p/itm123"},
        )
        assert resp.status_code == 422
        assert "Missing 'pid'" in resp.json()["detail"]

    app.dependency_overrides.clear()


@pytest.mark.anyio
async def test_analyze_url_supports_flipkart(async_session: AsyncSession) -> None:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        app_env="development",
        auth_enabled=False,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: async_session
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

    with TestClient(app) as client:
        url = (
            "https://www.flipkart.com/boat-airdopes-131/p/itm98765"
            "?pid=ACCGXYZ987654321"
        )
        resp = client.post(
            "/api/v1/harvester/analyze-url",
            json={"url": url},
        )
        assert resp.status_code == 200
        data = resp.json()

        assert data["asin"] == "ACCGXYZ987654321"
        assert "Boat Airdopes 131" in data["product"]["product_name"]
        assert data["price_history"]["observations_count"] >= 1
        assert data["insights"] is not None
        assert "Flipkart product resolved" in data["status_note"]

    app.dependency_overrides.clear()
