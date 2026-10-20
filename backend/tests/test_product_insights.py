"""Tests for Product Intelligence / Review Insights service and endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.core.database import Base, get_db
from app.main import create_app
from app.models.product import Product
from app.models.review import Review
from app.services.harvester.insights import compute_product_insights

# ---------------------------------------------------------------------------
# In-memory async SQLite fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def async_session() -> AsyncSession:  # type: ignore[misc]
    """Async SQLite in-memory session with all ORM tables created."""
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

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


# ---------------------------------------------------------------------------
# Unit tests for compute_product_insights
# ---------------------------------------------------------------------------


async def test_insights_nonexistent_product(async_session: AsyncSession) -> None:
    res = await compute_product_insights(async_session, "NONEXISTENT")
    assert res is None


async def test_insights_product_with_no_reviews(async_session: AsyncSession) -> None:
    prod = Product(
        product_id="PROD_NO_REV",
        product_name="Product Without Reviews",
        category="Computers",
        rating=4.2,
        rating_count=0,
    )
    async_session.add(prod)
    await async_session.commit()

    insights = await compute_product_insights(async_session, "PROD_NO_REV")
    assert insights is not None
    assert insights.product_id == "PROD_NO_REV"
    assert insights.product_name == "Product Without Reviews"
    assert insights.total_reviews_in_db == 0
    assert insights.total_reviews_analyzed == 0
    assert insights.ratings.average_rating == 4.2
    assert insights.sentiment.average_polarity == 0.0
    assert insights.sentiment.sentiment_label == "neutral"
    assert insights.top_topics == []
    assert insights.readability.average_reading_ease is None


async def test_insights_product_with_reviews_and_aspects(
    async_session: AsyncSession,
) -> None:
    prod = Product(
        product_id="PROD_1",
        product_name="Smart Noise Cancelling Headphones",
        category="Electronics",
        rating=4.5,
        rating_count=2,
    )
    async_session.add(prod)

    r1 = Review(
        review_id="REV_1",
        product_id="PROD_1",
        rating=5.0,
        review_title="Outstanding sound and battery",
        review_content=(
            "The battery life is amazing and lasts multiple days on one charge. "
            "Sound quality is crystal clear and very impressive!"
        ),
    )
    r2 = Review(
        review_id="REV_2",
        product_id="PROD_1",
        rating=2.0,
        review_title="Poor build durability",
        review_content=(
            "The build quality is terrible and feels very fragile. "
            "The hinge cracked after just one week of normal use."
        ),
    )
    async_session.add_all([r1, r2])
    await async_session.commit()

    insights = await compute_product_insights(
        async_session,
        "PROD_1",
        aspects=["battery", "build quality"],
    )

    assert insights is not None
    assert insights.total_reviews_in_db == 2
    assert insights.total_reviews_analyzed == 2
    assert insights.ratings.average_rating == 3.5  # (5.0 + 2.0) / 2
    assert insights.ratings.stars_5 == 1
    assert insights.ratings.stars_2 == 1

    # Sentiment checks
    assert insights.sentiment.counts.positive == 1
    assert insights.sentiment.counts.negative == 1
    assert len(insights.sentiment.top_positive_highlights) > 0

    # Aspect checks
    assert "battery" in insights.sentiment.aspects
    battery_aspect = insights.sentiment.aspects["battery"]
    assert battery_aspect.mentions_count == 2
    assert battery_aspect.label == "positive"
    assert battery_aspect.average_polarity > 0.0

    assert "build quality" in insights.sentiment.aspects
    build_aspect = insights.sentiment.aspects["build quality"]
    assert build_aspect.mentions_count == 1
    assert build_aspect.label == "negative"
    assert build_aspect.average_polarity < 0.0

    # Topics and readability
    assert len(insights.top_topics) > 0
    assert insights.readability.average_reading_ease is not None
    assert insights.readability.consensus_grade_level is not None


async def test_insights_limit_capping(async_session: AsyncSession) -> None:
    prod = Product(
        product_id="PROD_LIMIT",
        product_name="Sample Cable",
        category="Accessories",
        rating=4.0,
    )
    async_session.add(prod)

    for i in range(5):
        rev = Review(
            review_id=f"REV_L_{i}",
            product_id="PROD_LIMIT",
            rating=4.0,
            review_title=f"Review {i}",
            review_content="Good cable works well as described.",
        )
        async_session.add(rev)
    await async_session.commit()

    insights = await compute_product_insights(async_session, "PROD_LIMIT", limit=2)
    assert insights is not None
    assert insights.total_reviews_in_db == 5
    assert insights.total_reviews_analyzed == 2


# ---------------------------------------------------------------------------
# API endpoint tests with database session override
# ---------------------------------------------------------------------------


async def test_get_product_insights_api_200_and_404(
    async_session: AsyncSession, settings: Settings
) -> None:
    prod = Product(
        product_id="API_PROD",
        product_name="USB Hub",
        category="Electronics",
        rating=5.0,
    )
    rev = Review(
        review_id="API_REV_1",
        product_id="API_PROD",
        rating=5.0,
        review_title="Excellent hub",
        review_content="Works great with all my devices. Super reliable!",
    )
    async_session.add_all([prod, rev])
    await async_session.commit()

    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: Settings(
        database_url="sqlite+aiosqlite:///:memory:"
    )
    app.dependency_overrides[get_db] = lambda: async_session

    with TestClient(app) as client:
        # 404 test
        resp_404 = client.get("/api/v1/harvester/products/NOT_HERE/insights")
        assert resp_404.status_code == 404
        assert "not found" in resp_404.json()["detail"].lower()

        # 200 test with aspects query parameter
        resp_200 = client.get(
            "/api/v1/harvester/products/API_PROD/insights?aspects=devices&limit=50"
        )
        assert resp_200.status_code == 200
        data = resp_200.json()
        assert data["product_id"] == "API_PROD"
        assert data["product_name"] == "USB Hub"
        assert data["total_reviews_analyzed"] == 1
        assert data["sentiment"]["counts"]["positive"] == 1
        assert "devices" in data["sentiment"]["aspects"]

    app.dependency_overrides.clear()
