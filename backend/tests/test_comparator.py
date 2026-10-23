"""Tests for Cross-Platform Comparator (Amazon vs Flipkart)."""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.core.database import Base
from app.models.product import Product
from app.models.review import Review
from app.services.harvester.comparator import (
    _classify_aspects,
    compare_product_platforms,
)


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


def test_classify_aspects_fragrance() -> None:
    aspects = _classify_aspects("Fragrances & Perfumes", "Dior Sauvage Eau De Parfum")
    aspect_names = [a[0] for a in aspects]
    assert "Fragrance Longevity" in aspect_names
    assert "Sillage & Projection" in aspect_names
    assert "Batch Authenticity" in aspect_names


def test_classify_aspects_phone() -> None:
    aspects = _classify_aspects("Electronics | Smartphones", "Apple iPhone 15 Pro")
    aspect_names = [a[0] for a in aspects]
    assert "Camera & Video" in aspect_names
    assert "Battery Backup" in aspect_names
    assert "Build & Weight" in aspect_names


def test_classify_aspects_audio() -> None:
    aspects = _classify_aspects("Electronics | Audio", "Sony WH-1000XM5 Headphones")
    aspect_names = [a[0] for a in aspects]
    assert "Active Noise Canceling" in aspect_names
    assert "Sound Quality & Bass" in aspect_names


def test_compare_endpoint_no_db(client: TestClient) -> None:
    response = client.get("/api/v1/harvester/products/NONEXISTENT/compare")
    assert response.status_code == 503


@pytest.mark.anyio
async def test_compare_product_platforms_memory_db(async_session: AsyncSession) -> None:
    # Insert test product
    product = Product(
        product_id="TEST-IPHONE",
        product_name="Apple iPhone 15 Pro",
        category="Electronics | Smartphones",
        discounted_price=Decimal("120000.00"),
        actual_price=Decimal("130000.00"),
        rating=4.7,
        rating_count=5000,
        img_link="https://example.com/iphone.jpg",
    )
    async_session.add(product)

    # Add 1 Amazon review and 1 Flipkart review
    amz_rev = Review(
        review_id="amz_rev_1",
        product_id="TEST-IPHONE",
        rating=5.0,
        review_title="Superb Amazon Purchase",
        review_content="Fast prime delivery and stunning titanium feel.",
    )
    fk_rev = Review(
        review_id="fk_rev_1",
        product_id="TEST-IPHONE",
        rating=4.5,
        review_title="Great Flipkart Experience",
        review_content="Delivered with open box inspection.",
    )
    async_session.add(amz_rev)
    async_session.add(fk_rev)
    await async_session.commit()

    comparison = await compare_product_platforms(async_session, "TEST-IPHONE")
    assert comparison is not None
    assert comparison.product_id == "TEST-IPHONE"
    assert comparison.amazon.platform == "Amazon.in"
    assert comparison.flipkart.platform == "Flipkart"
    assert len(comparison.amazon.aspects) == 4
    assert len(comparison.flipkart.aspects) == 4
    assert len(comparison.amazon.top_reviews) >= 1
    assert len(comparison.flipkart.top_reviews) >= 1
    assert comparison.verdict.summary != ""
