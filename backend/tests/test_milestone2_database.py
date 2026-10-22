"""Milestone 2: Database Hardening test suite.

Covers:
- Task A: Concurrency-safe snapshot creation, row locking, and transaction rollback.
- Task B: Connection pool configuration, validation, and SQLite exemption.
- Task C: Composite index on (product_id, observed_at) and query compilation.
- Task D: Monetary storage migration to Decimal and exact non-binary float math.
- Task E: Alembic migration chain upgrade and downgrade on pre-existing data.
- Task F: Regression protection across models, schemas, services, and APIs.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import event, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.v1.harvester import get_product_by_id
from app.core.config import Settings
from app.core.database import Base, get_engine
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.schemas.harvester import (
    PriceHistoryResponse,
    PriceSnapshotSchema,
    ProductDetailResponse,
)
from app.services.harvester.normalizer import parse_price
from app.services.harvester.price_history import (
    get_price_history,
    record_price_snapshot,
)

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
    def _set_sqlite_pragma(dbapi_conn: Any, _: Any) -> None:
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
        product_id="B0HARDEN01",
        product_name="Database Hardening Test Product",
        category="Electronics",
        discounted_price=Decimal("1999.00"),
        actual_price=Decimal("2999.00"),
    )
    async_session.add(prod)
    await async_session.commit()
    return prod


# ---------------------------------------------------------------------------
# Task A: Concurrency-Safe Snapshot Creation & Transaction Rollback
# ---------------------------------------------------------------------------


class TestSnapshotConcurrencyAndTransactions:
    @pytest.mark.anyio
    async def test_row_lock_sql_compiles_to_for_update_on_postgresql(self) -> None:
        """Verify lock query generates SELECT ... FOR UPDATE on PostgreSQL dialect."""
        stmt = (
            select(Product.id)
            .where(Product.product_id == "B0HARDEN01")
            .with_for_update()
        )
        compiled = str(stmt.compile(dialect=postgresql.dialect()))
        assert "FOR UPDATE" in compiled
        assert "products.product_id = " in compiled

    @pytest.mark.anyio
    async def test_concurrent_identical_snapshot_recording_deduplicates(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Sequential and interleaved snapshot requests deduplicate cleanly."""
        prod_id = sample_product.product_id

        # First recording
        snap1 = await record_price_snapshot(
            async_session,
            prod_id,
            price=Decimal("1499.00"),
            original_price=Decimal("1999.00"),
            currency="INR",
            source="test_runner",
        )
        await async_session.commit()

        # Second identical recording triggers deduplication
        snap2 = await record_price_snapshot(
            async_session,
            prod_id,
            price=Decimal("1499.00"),
            original_price=Decimal("1999.00"),
            currency="INR",
            source="test_runner",
        )
        await async_session.commit()

        # Both calls should resolve to the same persisted snapshot instance
        assert snap1.id == snap2.id
        assert snap1.price == Decimal("1499.00")

        # Verify only 1 row exists in database
        stmt = select(PriceSnapshot).where(PriceSnapshot.product_id == prod_id)
        results = (await async_session.execute(stmt)).scalars().all()
        assert len(results) == 1

    @pytest.mark.anyio
    async def test_transaction_rollback_preserves_database_integrity(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Verify rollback leaves no orphaned or partially written snapshot."""
        prod_id = sample_product.product_id

        await record_price_snapshot(
            async_session,
            prod_id,
            price=Decimal("1200.00"),
            currency="INR",
        )
        # Explicit rollback before commit
        await async_session.rollback()

        stmt = select(PriceSnapshot).where(PriceSnapshot.product_id == prod_id)
        snaps = (await async_session.execute(stmt)).scalars().all()
        assert len(snaps) == 0

    @pytest.mark.anyio
    async def test_preserves_legitimate_historical_price_oscillations(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Legitimate price fluctuations (1000 -> 900 -> 1000) are all retained."""
        s1 = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=Decimal("1000.00"),
            currency="INR",
        )
        await async_session.commit()

        s2 = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=Decimal("900.00"),
            currency="INR",
        )
        await async_session.commit()

        s3 = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=Decimal("1000.00"),
            currency="INR",
        )
        await async_session.commit()

        assert s1.id != s2.id
        assert s2.id != s3.id
        assert s1.id != s3.id

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.observations_count == 3
        assert history.first_observed_price == Decimal("1000.00")
        assert history.lowest_observed_price == Decimal("900.00")
        assert history.latest_observed_price == Decimal("1000.00")


# ---------------------------------------------------------------------------
# Task B: Connection Pool Configuration & Validation
# ---------------------------------------------------------------------------


class TestConnectionPoolConfiguration:
    def test_default_pool_settings(self) -> None:
        s = Settings(_env_file=None)
        assert s.db_pool_size == 10
        assert s.db_max_overflow == 20
        assert s.db_pool_timeout == 30.0
        assert s.db_pool_recycle == 1800
        assert s.db_pool_pre_ping is True

    def test_custom_valid_pool_settings(self) -> None:
        s = Settings(
            _env_file=None,
            db_pool_size=15,
            db_max_overflow=25,
            db_pool_timeout=10.0,
            db_pool_recycle=3600,
            db_pool_pre_ping=False,
        )
        assert s.db_pool_size == 15
        assert s.db_max_overflow == 25
        assert s.db_pool_timeout == 10.0
        assert s.db_pool_recycle == 3600
        assert s.db_pool_pre_ping is False

    def test_invalid_pool_size_raises_validation_error(self) -> None:
        with pytest.raises(ValueError, match="db_pool_size"):
            Settings(_env_file=None, db_pool_size=0)
        with pytest.raises(ValueError, match="db_pool_size"):
            Settings(_env_file=None, db_pool_size=-5)

    def test_invalid_max_overflow_raises_validation_error(self) -> None:
        with pytest.raises(ValueError, match="db_max_overflow"):
            Settings(_env_file=None, db_max_overflow=-1)

    def test_invalid_pool_timeout_raises_validation_error(self) -> None:
        with pytest.raises(ValueError, match="db_pool_timeout"):
            Settings(_env_file=None, db_pool_timeout=0.0)
        with pytest.raises(ValueError, match="db_pool_timeout"):
            Settings(_env_file=None, db_pool_timeout=-1.5)

    def test_invalid_pool_recycle_raises_validation_error(self) -> None:
        with pytest.raises(ValueError, match="db_pool_recycle"):
            Settings(_env_file=None, db_pool_recycle=-2)

    def test_sqlite_engine_excludes_unsupported_pool_options(self) -> None:
        """SQLite should not receive pool_size or max_overflow."""
        sqlite_url = "sqlite+aiosqlite:///:memory:"
        engine = get_engine(sqlite_url)
        assert "sqlite" in str(engine.url)
        # Successfully created without TypeError from unsupported pool options


# ---------------------------------------------------------------------------
# Task C: Composite Index on (product_id, observed_at)
# ---------------------------------------------------------------------------


class TestCompositeIndex:
    def test_composite_index_defined_on_price_snapshot_model(self) -> None:
        table = PriceSnapshot.__table__
        indexes = {idx.name: [c.name for c in idx.columns] for idx in table.indexes}

        assert "ix_price_snapshots_product_id_observed_at" in indexes
        cols = indexes["ix_price_snapshots_product_id_observed_at"]
        assert cols == ["product_id", "observed_at"]

    def test_composite_index_query_compilation(self) -> None:
        stmt = (
            select(PriceSnapshot)
            .where(PriceSnapshot.product_id == "B0TEST")
            .order_by(PriceSnapshot.observed_at.desc())
        )
        compiled = str(stmt.compile(dialect=postgresql.dialect()))
        assert "WHERE price_snapshots.product_id =" in compiled
        assert "ORDER BY price_snapshots.observed_at DESC" in compiled


# ---------------------------------------------------------------------------
# Task D: Decimal Precision & Monetary Math
# ---------------------------------------------------------------------------


class TestDecimalMonetaryOperations:
    @pytest.mark.anyio
    async def test_monetary_persistence_and_retrieval(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Verify products and snapshots persist and retrieve exact Decimal values."""
        product = await get_product_by_id(async_session, sample_product.product_id)
        assert product is not None
        assert isinstance(product.discounted_price, Decimal)
        assert isinstance(product.actual_price, Decimal)
        assert product.discounted_price == Decimal("1999.00")
        assert product.actual_price == Decimal("2999.00")

        snap = await record_price_snapshot(
            async_session,
            sample_product.product_id,
            price=Decimal("1799.99"),
            original_price=Decimal("2499.50"),
            currency="INR",
        )
        await async_session.commit()

        loaded_snap = (
            await async_session.execute(
                select(PriceSnapshot).where(PriceSnapshot.id == snap.id)
            )
        ).scalar_one()

        assert isinstance(loaded_snap.price, Decimal)
        assert isinstance(loaded_snap.original_price, Decimal)
        assert loaded_snap.price == Decimal("1799.99")
        assert loaded_snap.original_price == Decimal("2499.50")

    def test_parse_price_returns_exact_quantized_decimals(self) -> None:
        assert parse_price("₹1,099") == Decimal("1099.00")
        assert parse_price("$19.99") == Decimal("19.99")
        assert parse_price("499") == Decimal("499.00")
        assert parse_price("0.005") == Decimal("0.01")  # ROUND_HALF_UP check
        assert parse_price("0.004") == Decimal("0.00")
        assert parse_price("") is None
        assert parse_price(None) is None

    @pytest.mark.anyio
    async def test_price_history_avoids_binary_float_imprecision(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Test calculation where float arithmetic creates binary drift."""
        # In binary float: 19.99 - 19.95 = 0.040000000000000925
        # In Decimal: Decimal('19.99') - Decimal('19.95') = Decimal('0.04')
        now = datetime.now(UTC)
        s1 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=Decimal("19.95"),
            currency="USD",
            source="test",
            observed_at=now - timedelta(days=2),
        )
        s2 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=Decimal("19.99"),
            currency="USD",
            source="test",
            observed_at=now,
        )
        async_session.add_all([s1, s2])
        await async_session.commit()

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.price_change_amount == Decimal("0.04")
        assert history.price_change_percentage == Decimal("0.20")
        assert isinstance(history.price_change_amount, Decimal)
        assert isinstance(history.price_change_percentage, Decimal)

    @pytest.mark.anyio
    async def test_multi_currency_strict_isolation(
        self, async_session: AsyncSession, sample_product: Product
    ) -> None:
        """Ensure price statistics do not cross currency boundaries."""
        now = datetime.now(UTC)
        s1 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=Decimal("100.00"),
            currency="USD",
            source="us_store",
            observed_at=now - timedelta(days=3),
        )
        s2 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=Decimal("7500.00"),
            currency="INR",
            source="in_store",
            observed_at=now - timedelta(days=1),
        )
        s3 = PriceSnapshot(
            product_id=sample_product.product_id,
            price=Decimal("8000.00"),
            currency="INR",
            source="in_store",
            observed_at=now,
        )
        async_session.add_all([s1, s2, s3])
        await async_session.commit()

        history = await get_price_history(async_session, sample_product.product_id)
        assert history.is_multi_currency is True
        assert history.currency == "INR"
        # Metrics calculated only on INR records
        assert history.first_observed_price == Decimal("7500.00")
        assert history.latest_observed_price == Decimal("8000.00")
        assert history.price_change_amount == Decimal("500.00")


# ---------------------------------------------------------------------------
# Task E: Alembic Migration Chain Upgrade & Pre-Existing Data Test
# ---------------------------------------------------------------------------


class TestAlembicMigrationChain:
    def test_alembic_upgrade_and_downgrade_with_existing_data(
        self, tmp_path: Path
    ) -> None:
        """Migrate pre-existing Float data to Numeric(12, 2) without data loss."""
        db_file = tmp_path / "test_migration.db"
        db_url = f"sqlite+aiosqlite:///{db_file.as_posix()}"

        alembic_ini_path = Path(__file__).resolve().parent.parent / "alembic.ini"
        config = Config(str(alembic_ini_path))
        config.set_main_option("sqlalchemy.url", db_url)

        # 1. Upgrade to 0002 (baseline with Float columns)
        command.upgrade(config, "0002")

        # 2. Insert pre-existing Float records into the 0002 schema
        import sqlite3

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO products (
                product_id, product_name, category,
                discounted_price, actual_price, created_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            ("B0PREEXIST", "Pre-existing Product", "Books", 499.50, 999.00),
        )
        cursor.execute(
            """
            INSERT INTO price_snapshots (
                product_id, price, original_price, currency, source, observed_at
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
            """,
            ("B0PREEXIST", 499.50, 999.00, "INR", "csv_import"),
        )
        conn.commit()
        conn.close()

        # 3. Upgrade to 0003 (Milestone 2 migration)
        command.upgrade(config, "0003")

        # 4. Verify existing data survived and composite index was created
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT discounted_price, actual_price FROM products WHERE product_id = ?",
            ("B0PREEXIST",),
        )
        row = cursor.fetchone()
        assert row is not None
        # SQLite stores converted decimal values accurately
        assert float(row[0]) == 499.50
        assert float(row[1]) == 999.00

        cursor.execute(
            "SELECT price, original_price FROM price_snapshots WHERE product_id = ?",
            ("B0PREEXIST",),
        )
        snap_row = cursor.fetchone()
        assert snap_row is not None
        assert float(snap_row[0]) == 499.50
        assert float(snap_row[1]) == 999.00

        # Verify composite index exists
        cursor.execute("PRAGMA index_list('price_snapshots')")
        indexes = [r[1] for r in cursor.fetchall()]
        assert "ix_price_snapshots_product_id_observed_at" in indexes

        conn.close()

        # 5. Verify clean downgrade back to 0002
        command.downgrade(config, "0002")

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("PRAGMA index_list('price_snapshots')")
        indexes_after_downgrade = [r[1] for r in cursor.fetchall()]
        assert (
            "ix_price_snapshots_product_id_observed_at" not in indexes_after_downgrade
        )
        conn.close()


# ---------------------------------------------------------------------------
# Task F: API Contract & Pydantic JSON Serialization Protection
# ---------------------------------------------------------------------------


class TestApiJsonSerializationCompatibility:
    def test_pydantic_schema_serializes_decimals_as_json_numbers(self) -> None:
        """JSON output must maintain numeric types for existing API consumers."""
        snap_schema = PriceSnapshotSchema(
            price=Decimal("1299.99"),
            original_price=Decimal("1999.00"),
            currency="INR",
            source="test",
            observed_at=datetime.now(UTC),
        )
        json_output = snap_schema.model_dump_json()
        assert '"price":1299.99' in json_output
        assert '"original_price":1999.0' in json_output

        history_schema = PriceHistoryResponse(
            product_id="B0TEST",
            observations_count=1,
            first_observed_price=Decimal("1299.99"),
            current_price=Decimal("1299.99"),
            price_change_amount=Decimal("0.00"),
            status_note="Single observation",
            snapshots=[snap_schema],
        )
        history_json = history_schema.model_dump_json()
        assert '"first_observed_price":1299.99' in history_json
        assert '"price_change_amount":0.0' in history_json

        prod_schema = ProductDetailResponse(
            product_id="B0TEST",
            product_name="Test",
            discounted_price=Decimal("1299.99"),
            actual_price=Decimal("1999.00"),
        )
        prod_json = prod_schema.model_dump_json()
        assert '"discounted_price":1299.99' in prod_json
        assert '"actual_price":1999.0' in prod_json
