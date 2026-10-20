"""Tests for the Review Harvester: normalizer, CSV adapter, importer, and API.

Test strategy
-------------
- Normalizer: pure functions, no fixtures needed.
- CSV adapter: uses a tiny in-memory CSV fixture (tmp_path).
- Importer / DB upserts: use an async SQLite in-memory DB via aiosqlite.
  No live PostgreSQL is required.
- API endpoints: monkeypatched DB dependency — tests the 503 (no DB configured)
  and 404 paths without touching a real database.

All tests are self-contained.  Run with:

    python -m pytest tests/test_harvester.py tests/test_harvester_api.py -v
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.collection_job import CollectionJob
from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
    SourceNotConfiguredError,
)
from app.services.harvester.csv_adapter import CsvAmazonAdapter
from app.services.harvester.importer import (
    run_csv_import,
    upsert_product,
    upsert_review,
    upsert_user,
)
from app.services.harvester.normalizer import (
    clean_text,
    parse_percentage,
    parse_price,
    parse_rating,
    parse_rating_count,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SAMPLE_CSV_HEADER = (
    "product_id,product_name,category,discounted_price,actual_price,"
    "discount_percentage,rating,rating_count,about_product,user_id,"
    "user_name,review_id,review_title,review_content,img_link,product_link"
)


def _make_csv_row(**kwargs: str) -> dict[str, str]:
    defaults = {
        "product_id": "TESTPROD01",
        "product_name": "Test Gadget",
        "category": "Electronics",
        "discounted_price": "₹499",
        "actual_price": "₹999",
        "discount_percentage": "50%",
        "rating": "4.5",
        "rating_count": "1,234",
        "about_product": "A great test gadget.",
        "user_id": "USER001",
        "user_name": "Alice",
        "review_id": "REV001",
        "review_title": "Excellent",
        "review_content": "Really happy with this product.",
        "img_link": "https://example.com/img.jpg",
        "product_link": "https://example.com/prod",
    }
    defaults.update(kwargs)
    return defaults


def _write_csv(tmp_path: Path, rows: list[dict[str, str]]) -> Path:
    csv_file = tmp_path / "test_amazon.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_make_csv_row().keys())
        writer.writeheader()
        writer.writerows(rows)
    return csv_file


# ---------------------------------------------------------------------------
# Async DB fixture (SQLite in-memory via aiosqlite)
# ---------------------------------------------------------------------------


@pytest.fixture
async def async_session() -> AsyncSession:  # type: ignore[misc]
    """Async SQLite in-memory session with all ORM tables created."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    # Enable FK enforcement in SQLite
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


# anyio_mode = "auto" in pyproject.toml handles all async test/fixture detection.


# ===========================================================================
# Normalizer tests (pure functions — no fixtures)
# ===========================================================================


class TestParsePrice:
    def test_rupee_with_comma(self) -> None:
        assert parse_price("₹1,099") == 1099.0

    def test_dollar(self) -> None:
        assert parse_price("$19.99") == 19.99

    def test_plain_float(self) -> None:
        assert parse_price("499") == 499.0

    def test_empty_string(self) -> None:
        assert parse_price("") is None

    def test_none(self) -> None:
        assert parse_price(None) is None

    def test_non_numeric(self) -> None:
        assert parse_price("N/A") is None

    def test_whitespace(self) -> None:
        assert parse_price("   ") is None


class TestParseRating:
    def test_valid_float(self) -> None:
        assert parse_rating("4.2") == 4.2

    def test_pipe_anomaly(self) -> None:
        """Row 1279 in amazon.csv has rating='|' — must return None."""
        assert parse_rating("|") is None

    def test_empty(self) -> None:
        assert parse_rating("") is None

    def test_none(self) -> None:
        assert parse_rating(None) is None

    def test_out_of_range_high(self) -> None:
        assert parse_rating("6.0") is None

    def test_out_of_range_low(self) -> None:
        assert parse_rating("-1.0") is None

    def test_zero(self) -> None:
        assert parse_rating("0.0") == 0.0

    def test_max(self) -> None:
        assert parse_rating("5.0") == 5.0


class TestParseRatingCount:
    def test_with_comma(self) -> None:
        assert parse_rating_count("24,269") == 24269

    def test_plain_int(self) -> None:
        assert parse_rating_count("100") == 100

    def test_empty(self) -> None:
        assert parse_rating_count("") is None

    def test_none(self) -> None:
        assert parse_rating_count(None) is None


class TestParsePercentage:
    def test_with_percent(self) -> None:
        assert parse_percentage("64%") == 64.0

    def test_without_percent(self) -> None:
        assert parse_percentage("50") == 50.0

    def test_empty(self) -> None:
        assert parse_percentage("") is None

    def test_none(self) -> None:
        assert parse_percentage(None) is None


class TestCleanText:
    def test_strips_whitespace(self) -> None:
        assert clean_text("  hello  ") == "hello"

    def test_empty_returns_none(self) -> None:
        assert clean_text("") is None

    def test_whitespace_only_returns_none(self) -> None:
        assert clean_text("   ") is None

    def test_none_returns_none(self) -> None:
        assert clean_text(None) is None

    def test_max_len_truncates(self) -> None:
        result = clean_text("abcdef", max_len=3)
        assert result == "abc"


# ===========================================================================
# CsvAmazonAdapter tests
# ===========================================================================


class TestCsvAmazonAdapter:
    def test_missing_file_raises(self) -> None:
        with pytest.raises(SourceNotConfiguredError):
            CsvAmazonAdapter("/nonexistent/path/amazon.csv")

    def test_yields_single_row(self, tmp_path: Path) -> None:
        csv_file = _write_csv(tmp_path, [_make_csv_row()])
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        assert len(records) == 1
        product, users, reviews = records[0]
        assert product.product_id == "TESTPROD01"
        assert product.rating == 4.5
        assert product.discounted_price == 499.0
        assert product.actual_price == 999.0
        assert product.discount_percentage == 50.0
        assert product.rating_count == 1234

    def test_skips_missing_product_id(self, tmp_path: Path) -> None:
        row = _make_csv_row(product_id="")
        csv_file = _write_csv(tmp_path, [row])
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        assert len(records) == 0

    def test_invalid_rating_becomes_none(self, tmp_path: Path) -> None:
        row = _make_csv_row(product_id="BAD001", review_id="RBAD01", rating="|")
        csv_file = _write_csv(tmp_path, [row])
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        assert len(records) == 1
        product, _, _ = records[0]
        assert product.rating is None

    def test_multi_review_row(self, tmp_path: Path) -> None:
        row = _make_csv_row(
            product_id="MULTI01",
            user_id="U1,U2",
            user_name="Alice,Bob",
            review_id="R1,R2",
            review_title="Good,Great",
            review_content="Loved it.",  # stored on first review only
        )
        csv_file = _write_csv(tmp_path, [row])
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        assert len(records) == 1
        _, users, reviews = records[0]
        assert len(reviews) == 2
        assert reviews[0].review_id == "R1"
        assert reviews[0].review_content == "Loved it."
        assert reviews[1].review_id == "R2"
        assert reviews[1].review_content is None  # only first review gets content

    def test_user_name_padding(self, tmp_path: Path) -> None:
        """When user_name count < user_id count, pad with 'Anonymous'."""
        row = _make_csv_row(
            product_id="PAD01",
            user_id="U1,U2,U3",
            user_name="Alice",  # only 1 name for 3 users
            review_id="R1,R2,R3",
            review_title="T1,T2,T3",
        )
        csv_file = _write_csv(tmp_path, [row])
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        _, users, _ = records[0]
        assert len(users) == 3
        assert users[0].user_name == "Alice"
        assert users[1].user_name == "Anonymous"
        assert users[2].user_name == "Anonymous"

    def test_multiple_rows(self, tmp_path: Path) -> None:
        rows = [
            _make_csv_row(product_id="P1", review_id="R1"),
            _make_csv_row(product_id="P2", review_id="R2"),
        ]
        csv_file = _write_csv(tmp_path, rows)
        adapter = CsvAmazonAdapter(str(csv_file))
        records = list(adapter.records())
        assert len(records) == 2


# ===========================================================================
# Importer / upsert tests (async, SQLite in-memory)
# ===========================================================================


class TestUpsertProduct:
    async def test_inserts_new_product(self, async_session: AsyncSession) -> None:
        p = NormalizedProduct(product_id="P001", product_name="Widget")
        inserted = await upsert_product(async_session, p)
        await async_session.commit()
        assert inserted is True

    async def test_idempotent_on_duplicate(self, async_session: AsyncSession) -> None:
        p = NormalizedProduct(product_id="P001", product_name="Widget")
        await upsert_product(async_session, p)
        await async_session.commit()
        inserted_again = await upsert_product(async_session, p)
        await async_session.commit()
        assert inserted_again is False

    async def test_price_and_rating_stored(self, async_session: AsyncSession) -> None:
        from sqlalchemy import select

        from app.models.product import Product

        p = NormalizedProduct(
            product_id="P002",
            product_name="Gadget",
            discounted_price=499.0,
            actual_price=999.0,
            rating=4.5,
            rating_count=1234,
        )
        await upsert_product(async_session, p)
        await async_session.commit()
        result = await async_session.execute(
            select(Product).where(Product.product_id == "P002")
        )
        row = result.scalar_one()
        assert row.discounted_price == 499.0
        assert row.rating == 4.5
        assert row.rating_count == 1234


class TestUpsertUser:
    async def test_inserts_new_user(self, async_session: AsyncSession) -> None:
        u = NormalizedUser(user_id="U001", user_name="Alice")
        inserted = await upsert_user(async_session, u)
        await async_session.commit()
        assert inserted is True

    async def test_idempotent_on_duplicate(self, async_session: AsyncSession) -> None:
        u = NormalizedUser(user_id="U001", user_name="Alice")
        await upsert_user(async_session, u)
        await async_session.commit()
        inserted_again = await upsert_user(async_session, u)
        await async_session.commit()
        assert inserted_again is False


class TestUpsertReview:
    async def _setup_product(self, session: AsyncSession) -> None:
        await upsert_product(
            session, NormalizedProduct(product_id="P001", product_name="W")
        )
        await session.commit()

    async def test_inserts_new_review(self, async_session: AsyncSession) -> None:
        await self._setup_product(async_session)
        r = NormalizedReview(review_id="REV001", product_id="P001")
        inserted = await upsert_review(async_session, r)
        await async_session.commit()
        assert inserted is True

    async def test_idempotent_on_duplicate(self, async_session: AsyncSession) -> None:
        await self._setup_product(async_session)
        r = NormalizedReview(review_id="REV001", product_id="P001")
        await upsert_review(async_session, r)
        await async_session.commit()
        inserted_again = await upsert_review(async_session, r)
        await async_session.commit()
        assert inserted_again is False

    async def test_review_content_stored(self, async_session: AsyncSession) -> None:
        from sqlalchemy import select

        from app.models.review import Review

        await self._setup_product(async_session)
        r = NormalizedReview(
            review_id="REV002",
            product_id="P001",
            review_title="Great",
            review_content="Really happy!",
        )
        await upsert_review(async_session, r)
        await async_session.commit()
        result = await async_session.execute(
            select(Review).where(Review.review_id == "REV002")
        )
        row = result.scalar_one()
        assert row.review_title == "Great"
        assert row.review_content == "Really happy!"


# ===========================================================================
# End-to-end run_csv_import tests
# ===========================================================================


class TestRunCsvImport:
    async def test_counts_match_fixture(
        self, async_session: AsyncSession, tmp_path: Path
    ) -> None:
        rows = [
            _make_csv_row(product_id="P1", review_id="R1"),
            _make_csv_row(product_id="P2", review_id="R2"),
        ]
        csv_file = _write_csv(tmp_path, rows)
        job = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job)
        await async_session.flush()

        await run_csv_import(async_session, str(csv_file), job)

        assert job.status == "done"
        assert job.products_seen == 2
        assert job.products_inserted == 2
        assert job.reviews_seen == 2
        assert job.reviews_inserted == 2
        assert job.error_count == 0

    async def test_repeat_run_is_safe(
        self, async_session: AsyncSession, tmp_path: Path
    ) -> None:
        """Running import twice: second run inserts nothing (idempotent)."""
        rows = [_make_csv_row(product_id="P1", review_id="R1")]
        csv_file = _write_csv(tmp_path, rows)

        job1 = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job1)
        await async_session.flush()
        await run_csv_import(async_session, str(csv_file), job1)
        assert job1.products_inserted == 1

        job2 = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job2)
        await async_session.flush()
        await run_csv_import(async_session, str(csv_file), job2)
        # Second run: rows seen again but not inserted (duplicate)
        assert job2.products_seen == 1
        assert job2.products_inserted == 0
        assert job2.reviews_seen == 1
        assert job2.reviews_inserted == 0
        assert job2.status == "done"

    async def test_invalid_rating_row_is_accepted_with_none(
        self, async_session: AsyncSession, tmp_path: Path
    ) -> None:
        """Row with bad rating should still produce a product with rating=None."""
        rows = [_make_csv_row(product_id="BADRATE", review_id="RBR1", rating="|")]
        csv_file = _write_csv(tmp_path, rows)
        job = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job)
        await async_session.flush()
        await run_csv_import(async_session, str(csv_file), job)

        assert job.status == "done"
        assert job.products_inserted == 1
        assert job.reviews_inserted == 1

        from sqlalchemy import select

        from app.models.product import Product

        result = await async_session.execute(
            select(Product).where(Product.product_id == "BADRATE")
        )
        p = result.scalar_one()
        assert p.rating is None

    async def test_missing_file_marks_job_failed(
        self, async_session: AsyncSession
    ) -> None:
        job = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job)
        await async_session.flush()
        await run_csv_import(async_session, "/nonexistent/file.csv", job)

        assert job.status == "failed"
        assert job.error_count >= 1

    async def test_multi_review_product_counts(
        self, async_session: AsyncSession, tmp_path: Path
    ) -> None:
        rows = [
            _make_csv_row(
                product_id="MULTI",
                user_id="U1,U2",
                user_name="Alice,Bob",
                review_id="R1,R2",
                review_title="Good,Great",
                review_content="Content here",
            )
        ]
        csv_file = _write_csv(tmp_path, rows)
        job = CollectionJob(source="csv_amazon", status="pending")
        async_session.add(job)
        await async_session.flush()
        await run_csv_import(async_session, str(csv_file), job)

        assert job.products_seen == 1
        assert job.products_inserted == 1
        assert job.reviews_seen == 2
        assert job.reviews_inserted == 2


# ===========================================================================
# CollectionJob.add_error helper
# ===========================================================================


class TestCollectionJobAddError:
    def test_adds_to_sample(self) -> None:
        job = CollectionJob(source="csv_amazon", status="pending")
        job.add_error("first error")
        assert job.error_count == 1
        assert "first error" in job.error_sample

    def test_caps_at_max(self) -> None:
        job = CollectionJob(source="csv_amazon", status="pending")
        for i in range(15):
            job.add_error(f"error {i}")
        assert job.error_count == 15
        import json

        sample = json.loads(job.error_sample)
        assert len(sample) == 10  # capped at 10
