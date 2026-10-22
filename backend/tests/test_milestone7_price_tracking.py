"""Milestone 7 comprehensive test suite for Price Tracking and Monitoring:
- Price snapshot recording validation & deduplication
- Price history calculations (first, latest, min, max, change amount/percentage,
  tracking period)
- Multi-currency guards (no misleading cross-currency math)
- Baseline peak logic (single observation is baseline, not historical peak)
- Date range filtering and validation
- API endpoints:
  - GET /api/v1/harvester/products/{product_id}/price-history
  - POST /api/v1/harvester/products/{product_id}/check-price
"""

from __future__ import annotations

import math
from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.auth import get_current_user, require_admin
from app.core.config import Settings, get_settings
from app.core.database import Base, get_db
from app.main import create_app
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.services.harvester.price_history import (
    get_price_history,
    poll_product_price,
    record_price_snapshot,
)
from app.services.harvester.provider import (
    MockProductDataProvider,
    ProductNotFoundError,
    ProviderAuthenticationError,
    ProviderCommunicationError,
    ProviderProduct,
    ProviderRateLimitError,
)
from tests.conftest import TEST_ADMIN_USER, TEST_USER

# ---------------------------------------------------------------------------
# Fixtures
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
async def sample_product(async_session: AsyncSession) -> Product:
    prod = Product(
        product_id="B0TESTPROD",
        product_name="Test Smart Gadget",
        category="Electronics",
        discounted_price=1999.0,
        actual_price=2999.0,
    )
    async_session.add(prod)
    await async_session.commit()
    return prod


# ---------------------------------------------------------------------------
# 1. Observation Integrity & Deduplication Tests
# ---------------------------------------------------------------------------


class TestObservationIntegrity:
    @pytest.mark.anyio
    async def test_record_price_validates_positive_finite(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        with pytest.raises(ValueError, match="positive, finite"):
            await record_price_snapshot(
                async_session, sample_product.product_id, price=0
            )

        with pytest.raises(ValueError, match="positive, finite"):
            await record_price_snapshot(
                async_session, sample_product.product_id, price=-50.0
            )

        with pytest.raises(ValueError, match="positive, finite"):
            await record_price_snapshot(
                async_session, sample_product.product_id, price=math.nan
            )

        with pytest.raises(ValueError, match="positive, finite"):
            await record_price_snapshot(
                async_session, sample_product.product_id, price=math.inf
            )

    @pytest.mark.anyio
    async def test_record_price_validates_currency(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        with pytest.raises(ValueError, match="Currency cannot be empty"):
            await record_price_snapshot(
                async_session, sample_product.product_id, price=100.0, currency="  "
            )

    @pytest.mark.anyio
    async def test_deduplication_prevents_identical_sequential_snapshots(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        # First recording
        snap1 = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=1999.0,
            original_price=2999.0,
            currency="INR",
            source="test_provider",
        )
        await async_session.commit()

        # Second identical recording
        snap2 = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=1999.0,
            original_price=2999.0,
            currency="INR",
            source="test_provider",
        )
        await async_session.commit()

        # Must return the existing snapshot without duplicating row
        assert snap1.id == snap2.id

        rows = (
            (
                await async_session.execute(
                    select(PriceSnapshot).where(
                        PriceSnapshot.product_id == sample_product.product_id
                    )
                )
            )
            .scalars()
            .all()
        )
        assert len(rows) == 1


# ---------------------------------------------------------------------------
# 2. Price History Calculations & Multi-Currency Guard Tests
# ---------------------------------------------------------------------------


class TestPriceHistoryCalculations:
    @pytest.mark.anyio
    async def test_empty_price_history(self, async_session: AsyncSession) -> None:
        history = await get_price_history(async_session, "B0NONEXISTENT")
        assert history.observations_count == 0
        assert history.first_observed_price is None
        assert history.latest_observed_price is None
        assert history.highest_observed_price is None
        assert history.lowest_observed_price is None
        assert history.price_change_amount is None
        assert history.price_change_percentage is None
        assert history.is_historical_peak is False
        assert "No price snapshots" in history.status_note

    @pytest.mark.anyio
    async def test_single_observation_is_baseline_not_peak(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        await record_price_snapshot(
            async_session, sample_product.product_id, price=1500.0, currency="INR"
        )
        await async_session.commit()

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.observations_count == 1
        assert history.first_observed_price == 1500.0
        assert history.latest_observed_price == 1500.0
        assert history.highest_observed_price == 1500.0
        assert history.lowest_observed_price == 1500.0
        assert history.price_change_amount == 0.0
        assert history.price_change_percentage == 0.0
        assert history.is_historical_peak is False
        assert "baseline, not a confirmed historical peak" in history.status_note

    @pytest.mark.anyio
    async def test_multiple_observations_price_trend(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        now = datetime.now(UTC)
        # Snapshot 1 (earliest): 2000 INR
        s1 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=2000.0,
            currency="INR",
            source="test",
            observed_at=now - timedelta(days=10),
        )
        # Snapshot 2: 1800 INR (lowest)
        s2 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1800.0,
            currency="INR",
            source="test",
            observed_at=now - timedelta(days=5),
        )
        # Snapshot 3: 2200 INR (highest and latest -> peak)
        s3 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=2200.0,
            currency="INR",
            source="test",
            observed_at=now,
        )
        async_session.add_all([s1, s2, s3])
        await async_session.commit()

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.observations_count == 3
        assert history.first_observed_price == 2000.0
        assert history.latest_observed_price == 2200.0
        assert history.highest_observed_price == 2200.0
        assert history.lowest_observed_price == 1800.0
        assert history.price_change_amount == 200.0  # 2200 - 2000
        assert history.price_change_percentage == 10.0  # +10%
        assert history.is_historical_peak is True
        assert history.tracking_period_days == 10.0

    @pytest.mark.anyio
    async def test_multi_currency_guard(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        # Snapshots in INR and USD
        s_inr1 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1500.0,
            currency="INR",
            source="inr_source",
            observed_at=datetime.now(UTC) - timedelta(days=2),
        )
        s_usd = PriceSnapshot(
            product_id=sample_product.product_id,
            price=25.0,  # 25 USD should not be treated as lowest price in INR!
            currency="USD",
            source="usd_source",
            observed_at=datetime.now(UTC) - timedelta(days=1),
        )
        s_inr2 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1600.0,
            currency="INR",
            source="inr_source",
            observed_at=datetime.now(UTC),
        )
        async_session.add_all([s_inr1, s_usd, s_inr2])
        await async_session.commit()

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.is_multi_currency is True
        assert history.currency == "INR"
        # Math must NOT use the 25 USD point for lowest price
        assert history.lowest_observed_price == 1500.0
        assert history.highest_observed_price == 1600.0
        assert history.first_observed_price == 1500.0
        assert history.latest_observed_price == 1600.0
        assert "Multi-currency observations detected" in history.status_note

    @pytest.mark.anyio
    async def test_date_range_filtering_and_validation(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        now = datetime.now(UTC)
        s_old = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1000.0,
            observed_at=now - timedelta(days=30),
        )
        s_mid = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1200.0,
            observed_at=now - timedelta(days=15),
        )
        s_new = PriceSnapshot(
            product_id=sample_product.product_id,
            price=1400.0,
            observed_at=now,
        )
        async_session.add_all([s_old, s_mid, s_new])
        await async_session.commit()

        # Validation: start_date > end_date raises ValueError
        with pytest.raises(ValueError, match="start_date cannot be after end_date"):
            await get_price_history(
                async_session,
                sample_product.product_id,
                start_date=now,
                end_date=now - timedelta(days=1),
            )

        # Filtering: between 20 days ago and 5 days ago
        filtered = await get_price_history(
            async_session,
            sample_product.product_id,
            start_date=now - timedelta(days=20),
            end_date=now - timedelta(days=5),
        )
        assert filtered.observations_count == 1
        assert filtered.first_observed_price == 1200.0


# ---------------------------------------------------------------------------
# 3. Provider Polling Service Tests
# ---------------------------------------------------------------------------


class TestProviderPolling:
    @pytest.mark.anyio
    async def test_poll_product_price_records_snapshot(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        provider = MockProductDataProvider(
            products={
                sample_product.product_id: ProviderProduct(
                    asin=sample_product.product_id,
                    title="Live Checked Item",
                    current_price=1750.0,
                    original_price=2499.0,
                    currency="INR",
                    source_name="mock_feed",
                )
            }
        )
        snap = await poll_product_price(async_session, sample_product, provider)
        assert snap is not None
        assert snap.price == 1750.0
        assert snap.currency == "INR"

    @pytest.mark.anyio
    async def test_poll_product_price_skips_when_no_price(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        provider = MockProductDataProvider(
            products={
                sample_product.product_id: ProviderProduct(
                    asin=sample_product.product_id,
                    title="No Price Item",
                    current_price=None,
                )
            }
        )
        snap = await poll_product_price(async_session, sample_product, provider)
        assert snap is None


# ---------------------------------------------------------------------------
# 4. API Endpoints Tests
# ---------------------------------------------------------------------------


class TestPriceHistoryEndpoints:
    @pytest.mark.anyio
    async def test_get_price_history_api_200(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=1999.0,
            original_price=2999.0,
        )
        await async_session.commit()

        settings = Settings(_env_file=None, database_url="sqlite+aiosqlite:///:memory:")
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[get_current_user] = lambda: TEST_USER

        with TestClient(app) as client:
            res = client.get(
                f"/api/v1/harvester/products/{sample_product.product_id}/price-history"
            )
            assert res.status_code == 200
            data = res.json()
            assert data["product_id"] == sample_product.product_id
            assert data["observations_count"] == 1
            assert data["first_observed_price"] == 1999.0
            assert data["latest_observed_price"] == 1999.0
            assert data["price_change_amount"] == 0.0

    @pytest.mark.anyio
    async def test_get_price_history_missing_product_404(
        self, async_session: AsyncSession
    ) -> None:
        settings = Settings(_env_file=None, database_url="sqlite+aiosqlite:///:memory:")
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[get_current_user] = lambda: TEST_USER

        with TestClient(app) as client:
            res = client.get("/api/v1/harvester/products/NONEXISTENT01/price-history")
            assert res.status_code == 404
            assert "not found" in res.json()["detail"].lower()

    @pytest.mark.anyio
    async def test_get_price_history_invalid_date_range_422(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        settings = Settings(_env_file=None, database_url="sqlite+aiosqlite:///:memory:")
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[get_current_user] = lambda: TEST_USER

        with TestClient(app) as client:
            res = client.get(
                f"/api/v1/harvester/products/{sample_product.product_id}/price-history",
                params={
                    "start_date": "2026-10-20T10:00:00Z",
                    "end_date": "2026-10-10T10:00:00Z",
                },
            )
            assert res.status_code == 422
            assert "start_date cannot be after end_date" in res.json()["detail"]

    @pytest.mark.anyio
    async def test_check_price_api_success(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        mock_provider = MockProductDataProvider(
            products={
                sample_product.product_id: ProviderProduct(
                    asin=sample_product.product_id,
                    title=sample_product.product_name,
                    current_price=1699.0,
                    original_price=2999.0,
                    currency="INR",
                    source_name="mock_api",
                )
            }
        )

        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="mock",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

        from unittest.mock import patch

        with (
            patch(
                "app.api.v1.harvester.get_product_provider",
                return_value=mock_provider,
            ),
            TestClient(app) as client,
        ):
            res = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert res.status_code == 200
            data = res.json()
            assert data["observations_count"] >= 1
            assert data["latest_observed_price"] == 1699.0

    @pytest.mark.anyio
    async def test_check_price_api_provider_errors(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        mock_provider = MockProductDataProvider()

        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="mock",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

        from unittest.mock import patch

        with (
            patch(
                "app.api.v1.harvester.get_product_provider",
                return_value=mock_provider,
            ),
            TestClient(app) as client,
        ):
            # 1. ProductNotFoundError -> 404
            mock_provider.set_error(
                sample_product.product_id, ProductNotFoundError("Not found")
            )
            r_404 = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert r_404.status_code == 404

            # 2. ProviderAuthenticationError -> 502
            mock_provider.set_error(
                sample_product.product_id, ProviderAuthenticationError("Bad key")
            )
            r_auth = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert r_auth.status_code == 502

            # 3. ProviderRateLimitError -> 429
            mock_provider.set_error(
                sample_product.product_id, ProviderRateLimitError("Rate limit")
            )
            r_rate = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert r_rate.status_code == 429

            # 4. ProviderCommunicationError -> 502
            mock_provider.set_error(
                sample_product.product_id, ProviderCommunicationError("Timeout")
            )
            r_comm = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert r_comm.status_code == 502

    @pytest.mark.anyio
    async def test_check_price_disabled_provider_returns_503(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+aiosqlite:///:memory:",
            amazon_provider="disabled",
        )
        app = create_app(settings)
        app.dependency_overrides[get_settings] = lambda: settings
        app.dependency_overrides[get_db] = lambda: async_session
        app.dependency_overrides[require_admin] = lambda: TEST_ADMIN_USER

        with TestClient(app) as client:
            res = client.post(
                f"/api/v1/harvester/products/{sample_product.product_id}/check-price"
            )
            assert res.status_code == 503
            assert "provider is not configured" in res.json()["detail"].lower()
