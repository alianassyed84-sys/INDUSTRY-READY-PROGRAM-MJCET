"""Unit tests for n8n web scraping callback and defect simulation endpoints."""

from collections.abc import AsyncGenerator, Generator
from decimal import Decimal
import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

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


def test_n8n_webhook_callback(client: TestClient) -> None:
    """Ensure n8n webhook callback accepts payload and records intelligence."""
    payload = {
        "product_id": "TEST_BOAT_141",
        "product_url": "https://www.amazon.in/dp/B09XS7JWHH",
        "platform": "amazon",
        "reviews_analyzed_count": 25,
        "ai_intelligence": {
            "product_summary": {
                "title": "boAt Airdopes 141",
                "current_rating": 3.4,
                "current_grade": "C",
            },
            "producer_insights": {
                "primary_bottleneck_type": "product_defect",
                "bottleneck_summary": "Battery degradation accounts for 65% of negative feedback.",
                "defects": [
                    {
                        "id": "battery_power",
                        "label": "Battery & Charging Failure",
                        "category": "hardware",
                        "complaint_percentage": 65.0,
                        "negative_mentions_count": 14,
                        "severity": "critical",
                        "evidence_snippets": ["Battery drains in 30 mins"],
                        "potential_rating_gain": 0.8,
                        "projected_rating_if_fixed": 4.2,
                        "projected_grade_if_fixed": "A",
                    }
                ],
                "what_if_full_resolution": {
                    "all_defects_fixed_rating": 4.5,
                    "all_defects_fixed_grade": "A+",
                },
            },
            "consumer_advisor": {
                "verdict": "AVOID_DEFECT",
                "deal_score": 52,
                "verdict_reason": "High battery defect rate reported by multiple verified buyers.",
                "honest_pros": ["Punchy bass", "Affordable"],
                "honest_cons": ["Battery dies quickly"],
                "critical_warning": "Warning: 65% of negative reviews cite battery failure.",
            },
        },
    }

    res = client.post("/api/v1/harvester/n8n/webhook-callback", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["product_id"] == "TEST_BOAT_141"
    assert data["producer_insights"]["defects"][0]["id"] == "battery_power"
    assert data["consumer_advisor"]["verdict"] == "AVOID_DEFECT"


def test_n8n_endpoints_no_db_returns_503(client: TestClient) -> None:
    """When no database is configured, n8n DB endpoints return 503."""
    res_get = client.get("/api/v1/harvester/products/AMZN-KAG-005/n8n-intelligence")
    assert res_get.status_code == 503

    res_post = client.post("/api/v1/harvester/n8n/trigger", json={"product_id": "TEST"})
    assert res_post.status_code == 503


@pytest.mark.anyio
async def test_get_n8n_intelligence_endpoint_with_db(async_session: AsyncSession) -> None:
    """Ensure retrieving intelligence for a seeded product computes from real reviews."""
    prod = Product(
        product_id="TEST_BOAT_LIVE",
        product_name="boAt Airdopes 141 ANC",
        category="Audio",
        discounted_price=Decimal("1499.00"),
        actual_price=Decimal("4490.00"),
        discount_percentage=66.6,
        rating=3.6,
        rating_count=120,
        product_link="https://www.amazon.in/dp/B09XS7JWHH",
    )
    async_session.add(prod)
    for i in range(5):
        rev = Review(
            review_id=f"rev_{i}",
            product_id="TEST_BOAT_LIVE",
            rating=2.0 if i < 3 else 4.0,
            review_title="Battery draining too fast" if i < 3 else "Good sound",
            review_content="Battery only lasts 40 minutes after one week." if i < 3 else "Decent sound quality.",
        )
        async_session.add(rev)
    await async_session.commit()

    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///:memory:",
        app_env="development",
        auth_enabled=False,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: async_session
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

    with TestClient(app) as tc:
        res = tc.get("/api/v1/harvester/products/TEST_BOAT_LIVE/n8n-intelligence")
        assert res.status_code == 200
        data = res.json()
        assert "producer_insights" in data
        assert "consumer_advisor" in data
        assert "defects" in data["producer_insights"]
        assert "deal_score" in data["consumer_advisor"]


@pytest.mark.anyio
async def test_n8n_trigger_with_url_not_found(async_session: AsyncSession) -> None:
    """Ensure triggering with an unknown product without reviews yields 404."""
    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///:memory:",
        app_env="development",
        auth_enabled=False,
    )
    app = create_app(settings)
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = lambda: async_session
    app.dependency_overrides[get_current_user] = lambda: TEST_USER
    app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

    with TestClient(app) as tc:
        res = tc.post(
            "/api/v1/harvester/n8n/trigger",
            json={"product_id": "NON_EXISTENT_PROD_123"},
        )
        assert res.status_code == 404
