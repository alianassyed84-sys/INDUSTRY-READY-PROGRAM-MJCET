"""Milestone 6 comprehensive verification test suite:
- Provider abstraction & error handling
- Mock & disabled provider configurations
- Price snapshot persistence and history calculation (no fabricated data)
- POST /api/v1/harvester/analyze-url on-demand pipeline
- End-to-end NLP review insights integration
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings, get_settings
from app.core.database import Base, get_db
from app.main import create_app
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.review import Review
from app.services.harvester.authorized_provider import AmazonCreatorApiProvider
from app.services.harvester.price_history import (
    get_price_history,
    record_price_snapshot,
)
from app.services.harvester.provider import (
    DisabledProductDataProvider,
    MockProductDataProvider,
    ProductNotFoundError,
    ProviderAuthenticationError,
    ProviderCommunicationError,
    ProviderNotConfiguredError,
    ProviderProduct,
    ProviderRateLimitError,
    ProviderReview,
    get_product_provider,
)

# ---------------------------------------------------------------------------
# In-memory async SQLite fixture
# ---------------------------------------------------------------------------


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

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.fixture
def mock_provider() -> MockProductDataProvider:
    sample_product = ProviderProduct(
        asin="B084J4MZK6",
        title="Echo Dot (4th Gen) Smart speaker with Alexa",
        currency="INR",
        current_price=2499.0,
        original_price=4499.0,
        discount_percentage=44.0,
        rating=4.4,
        rating_count=320,
        category="Electronics|SmartSpeakers",
        about_product=(
            "Voice control your entertainment - Stream audio from Amazon Music, "
            "Spotify."
        ),
        img_url="https://m.media-amazon.com/images/I/61KIy6gX-CL._SL1000_.jpg",
        product_url="https://www.amazon.in/dp/B084J4MZK6",
        reviews=(
            ProviderReview(
                review_id="R1ECHO",
                rating=5.0,
                review_title="Excellent sound and smart features",
                review_content=(
                    "The audio clarity is great and Alexa hears commands accurately."
                ),
                user_id="U1ECHO",
                user_name="Rahul",
            ),
            ProviderReview(
                review_id="R2ECHO",
                rating=4.0,
                review_title="Good compact speaker",
                review_content=(
                    "Bass is adequate for small bedrooms. Build quality is sturdy."
                ),
                user_id="U2ECHO",
                user_name="Priya",
            ),
        ),
        source_name="mock_provider",
    )
    return MockProductDataProvider(products={"B084J4MZK6": sample_product})


# ---------------------------------------------------------------------------
# 1. Provider Abstraction & Configuration Tests
# ---------------------------------------------------------------------------


class TestProviderAbstraction:
    @pytest.mark.anyio
    async def test_mock_provider_fetches_seeded_product(
        self, mock_provider: MockProductDataProvider
    ) -> None:
        product = await mock_provider.get_product_by_asin("B084J4MZK6")
        assert product is not None
        assert product.asin == "B084J4MZK6"
        assert product.current_price == 2499.0
        assert len(product.reviews) == 2

    @pytest.mark.anyio
    async def test_mock_provider_returns_none_for_unknown_asin(
        self, mock_provider: MockProductDataProvider
    ) -> None:
        assert await mock_provider.get_product_by_asin("B000000000") is None

    @pytest.mark.anyio
    async def test_mock_provider_raises_configured_exception(
        self, mock_provider: MockProductDataProvider
    ) -> None:
        mock_provider.set_error(
            "B0ERROR123", ProviderRateLimitError("Rate limit exceeded")
        )
        with pytest.raises(ProviderRateLimitError, match="Rate limit"):
            await mock_provider.get_product_by_asin("B0ERROR123")

    @pytest.mark.anyio
    async def test_disabled_provider_raises_error(self) -> None:
        provider = DisabledProductDataProvider()
        with pytest.raises(
            ProviderNotConfiguredError, match="No product data provider"
        ):
            await provider.get_product_by_asin("B084J4MZK6")

    def test_provider_factory_resolution(self) -> None:
        s_disabled = Settings(_env_file=None, amazon_provider="disabled")
        assert isinstance(get_product_provider(s_disabled), DisabledProductDataProvider)

        s_mock = Settings(_env_file=None, amazon_provider="mock")
        assert isinstance(get_product_provider(s_mock), MockProductDataProvider)

        s_creator = Settings(
            _env_file=None,
            amazon_provider="creator_api",
            amazon_access_key="AKIAIOSFODNN7EXAMPLE",
            amazon_secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            amazon_partner_tag="reviewpulse-21",
        )
        assert isinstance(get_product_provider(s_creator), AmazonCreatorApiProvider)


# ---------------------------------------------------------------------------
# 2. Authorized Provider Verification & Blocker Handling (Milestone 6C)
# ---------------------------------------------------------------------------


class TestAuthorizedProviderBlockers:
    def test_missing_credentials_raises_not_configured_error(self) -> None:
        provider = AmazonCreatorApiProvider(
            access_key=None, secret_key=None, partner_tag=None
        )
        with pytest.raises(ProviderNotConfiguredError) as exc_info:
            provider._verify_credentials()
        msg = str(exc_info.value)
        assert "AMAZON_ACCESS_KEY" in msg
        assert "AMAZON_SECRET_KEY" in msg
        assert "AMAZON_PARTNER_TAG" in msg

    def test_malformed_access_key_raises_auth_error(self) -> None:
        provider = AmazonCreatorApiProvider(
            access_key="short_key",
            secret_key="secret",
            partner_tag="tag",
        )
        with pytest.raises(
            ProviderAuthenticationError, match="Invalid AMAZON_ACCESS_KEY format"
        ):
            provider._verify_credentials()

    @pytest.mark.anyio
    async def test_live_call_raises_documented_blocker(self) -> None:
        provider = AmazonCreatorApiProvider(
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
            partner_tag="reviewpulse-21",
        )
        with pytest.raises(
            ProviderNotConfiguredError, match="account has not been verified"
        ):
            await provider.get_product_by_asin("B084J4MZK6")


# ---------------------------------------------------------------------------
# 3. Price Snapshot & Price History Calculation (Milestone 6E)
# ---------------------------------------------------------------------------


class TestPriceHistoryCalculation:
    @pytest.mark.anyio
    async def test_empty_snapshots_returns_zero_observations(
        self, async_session: AsyncSession
    ) -> None:
        history = await get_price_history(async_session, "B0EMPTY0000")
        assert history.observations_count == 0
        assert history.highest_observed_price is None
        assert history.lowest_observed_price is None
        assert history.is_historical_peak is False

    @pytest.mark.anyio
    async def test_single_snapshot_never_claims_historical_peak(
        self, async_session: AsyncSession
    ) -> None:
        prod = Product(product_id="B0SINGLE01", product_name="Single Snapshot Item")
        async_session.add(prod)
        await async_session.commit()

        await record_price_snapshot(
            async_session,
            product_id="B0SINGLE01",
            price=1999.0,
            original_price=2999.0,
            currency="INR",
            source="test",
        )
        await async_session.commit()

        history = await get_price_history(async_session, "B0SINGLE01")
        assert history.observations_count == 1
        assert history.current_price == 1999.0
        assert history.highest_observed_price == 1999.0
        assert history.lowest_observed_price == 1999.0
        # Critical constraint: a single observation must not claim a peak
        assert history.is_historical_peak is False
        assert "insufficient history" in history.status_note.lower()

    @pytest.mark.anyio
    async def test_multiple_snapshots_detect_peak_from_recorded_data(
        self, async_session: AsyncSession
    ) -> None:
        prod = Product(product_id="B0MULTI001", product_name="Multi Snapshot Item")
        async_session.add(prod)
        await async_session.commit()

        # Snapshot 1: 1500
        await record_price_snapshot(async_session, "B0MULTI001", price=1500.0)
        # Snapshot 2: 1200 (discounted)
        await record_price_snapshot(async_session, "B0MULTI001", price=1200.0)
        # Snapshot 3: 1600 (peak observed price)
        await record_price_snapshot(async_session, "B0MULTI001", price=1600.0)
        await async_session.commit()

        history = await get_price_history(async_session, "B0MULTI001")
        assert history.observations_count == 3
        assert history.current_price == 1600.0
        assert history.highest_observed_price == 1600.0
        assert history.lowest_observed_price == 1200.0
        assert history.is_historical_peak is True


# ---------------------------------------------------------------------------
# 4. On-Demand Analysis API Endpoint (Milestone 6D & 6F)
# ---------------------------------------------------------------------------


class TestAnalyzeUrlEndpoint:
    def test_endpoint_in_openapi_schema(self, client: TestClient) -> None:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        assert "/api/v1/harvester/analyze-url" in response.json()["paths"]

    def test_no_database_returns_503(self) -> None:
        settings = Settings(
            _env_file=None,
            database_url=None,
            cors_origins=["http://localhost:3000"],
        )
        get_settings.cache_clear()
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        with TestClient(app) as test_client:
            res = test_client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B084J4MZK6"},
            )
            assert res.status_code == 503
            assert "Database is not configured" in res.json()["detail"]

    @pytest.mark.anyio
    async def test_invalid_url_returns_422(self, async_session: AsyncSession) -> None:
        settings = Settings(_env_file=None, database_url="sqlite+aiosqlite:///:memory:")
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session

        with TestClient(app) as client:
            res = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "http://insecure-domain.com/dp/B084J4MZK6"},
            )
            assert res.status_code == 422
            assert "Invalid Amazon.in URL" in res.json()["detail"]

    @pytest.mark.anyio
    async def test_unconfigured_provider_returns_503(
        self, async_session: AsyncSession
    ) -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="disabled",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session

        with TestClient(app) as client:
            res = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B0UNKNOWN1"},
            )
            assert res.status_code == 503
            assert "provider is not configured" in res.json()["detail"]

    @pytest.mark.anyio
    async def test_mock_provider_end_to_end_analysis(
        self, async_session: AsyncSession, mock_provider: MockProductDataProvider
    ) -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="mock",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session

        # Inject our mock provider fixture into the API route handler
        from unittest.mock import patch

        with (
            patch(
                "app.api.v1.harvester.get_product_provider",
                return_value=mock_provider,
            ),
            TestClient(app) as client,
        ):
            res = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/Echo-Dot/dp/B084J4MZK6?ref=sr_1_1"},
            )
            assert res.status_code == 200
            data = res.json()

            # ASIN & Canonical URL
            assert data["asin"] == "B084J4MZK6"
            assert data["canonical_url"] == "https://www.amazon.in/dp/B084J4MZK6"

            # Product Detail
            prod = data["product"]
            assert prod["product_id"] == "B084J4MZK6"
            assert prod["discounted_price"] == 2499.0
            assert prod["actual_price"] == 4499.0

            # Price History
            history = data["price_history"]
            assert history["observations_count"] >= 1
            assert history["current_price"] == 2499.0

            # Review NLP Insights
            insights = data["insights"]
            assert insights is not None
            assert insights["total_reviews_analyzed"] == 2
            assert insights["ratings"]["total_ratings_count"] == 2
            assert insights["sentiment"]["counts"]["positive"] >= 1
            assert "Analysis complete based on 2 review(s)" in data["status_note"]

            # Database persistence verification
            db_prod = (
                await async_session.execute(
                    select(Product).where(Product.product_id == "B084J4MZK6")
                )
            ).scalar_one_or_none()
            assert db_prod is not None

            db_reviews = (
                (
                    await async_session.execute(
                        select(Review).where(Review.product_id == "B084J4MZK6")
                    )
                )
                .scalars()
                .all()
            )
            assert len(db_reviews) == 2

            db_snapshots = (
                (
                    await async_session.execute(
                        select(PriceSnapshot).where(
                            PriceSnapshot.product_id == "B084J4MZK6"
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(db_snapshots) >= 1

    @pytest.mark.anyio
    async def test_reanalyzing_existing_product_does_not_duplicate(
        self, async_session: AsyncSession, mock_provider: MockProductDataProvider
    ) -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="mock",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session

        from unittest.mock import patch

        with (
            patch(
                "app.api.v1.harvester.get_product_provider",
                return_value=mock_provider,
            ),
            TestClient(app) as client,
        ):
            # First call: populates DB
            res1 = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B084J4MZK6"},
            )
            assert res1.status_code == 200

            # Second call: re-analyzes already stored product
            res2 = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B084J4MZK6"},
            )
            assert res2.status_code == 200

            # Confirm no duplicate products in database
            count = len(
                (
                    await async_session.execute(
                        select(Product).where(Product.product_id == "B084J4MZK6")
                    )
                )
                .scalars()
                .all()
            )
            assert count == 1

    @pytest.mark.anyio
    async def test_provider_errors_mapped_to_proper_http_statuses(
        self, async_session: AsyncSession, mock_provider: MockProductDataProvider
    ) -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="mock",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session

        from unittest.mock import patch

        with (
            patch(
                "app.api.v1.harvester.get_product_provider",
                return_value=mock_provider,
            ),
            TestClient(app) as client,
        ):
            # 1. ProductNotFoundError -> 404
            mock_provider.set_error("B0NOTFND01", ProductNotFoundError("Not found"))
            r_404 = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B0NOTFND01"},
            )
            assert r_404.status_code == 404

            # 2. ProviderAuthenticationError -> 502
            mock_provider.set_error(
                "B0BDAUTH01", ProviderAuthenticationError("Bad credentials")
            )
            r_auth = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B0BDAUTH01"},
            )
            assert r_auth.status_code == 502

            # 3. ProviderRateLimitError -> 429
            mock_provider.set_error(
                "B0RATELM01", ProviderRateLimitError("Rate limit exceeded")
            )
            r_rate = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B0RATELM01"},
            )
            assert r_rate.status_code == 429

            # 4. ProviderCommunicationError -> 502
            mock_provider.set_error(
                "B0COMMER01", ProviderCommunicationError("Network timeout")
            )
            r_comm = client.post(
                "/api/v1/harvester/analyze-url",
                json={"url": "https://www.amazon.in/dp/B0COMMER01"},
            )
            assert r_comm.status_code == 502
