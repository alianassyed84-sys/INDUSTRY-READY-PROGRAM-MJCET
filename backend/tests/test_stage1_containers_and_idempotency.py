"""Stage 1 tests: Unmatched containers, no batching, no fake users/stars, idempotent hash review_id."""

import io
from collections.abc import AsyncGenerator
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.product import Product
from app.models.review import Review
from app.services.harvester.csv_adapter import CsvAmazonAdapter, _hash_review_content
from app.services.harvester.importer import list_products


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


def test_review_content_hash_is_deterministic_and_not_position_based():
    """Assertion: review_id must be a content hash of normalized title+body, not position-based."""
    title = "  Great Sound!  "
    body = "  These headphones are amazing for the price.  "

    hash_id_1 = _hash_review_content(title, body)
    hash_id_2 = _hash_review_content("great sound!", "these headphones are amazing for the price.")
    assert hash_id_1 == hash_id_2, "Normalized title and body must produce identical hash IDs"
    assert not hash_id_1.startswith("kag_rev_"), "review_id must not be position-based (kag_rev_NNN)"


def test_kaggle_polarity_no_fake_batching_and_no_fake_users_or_stars():
    """Assertion: Polarity dataset rows must not create fake products, fake prices, fake users, or fake stars."""
    csv_data = (
        "2,\"Great Sound\",\"Loved the bass and battery life\"\n"
        "1,\"Terrible\",\"Stopped working after one day\"\n"
    )
    fh = io.StringIO(csv_data)
    adapter = CsvAmazonAdapter.__new__(CsvAmazonAdapter)
    adapter.reviews_per_product = 50
    records = list(adapter._parse_kaggle_polarity(fh, import_job_id=1, category="Audio"))

    # Must produce one container (or records under an unmatched_group container), NOT AMZN-KAG-001
    assert len(records) == 1, "Should yield a single container tuple for the import category"
    for product, users, reviews in records:
        assert not product.product_id.startswith("AMZN-KAG-"), "Must not create fake AMZN-KAG batches"
        assert product.kind == "unmatched_group", "Polarity data without product identity must be kind='unmatched_group'"
        assert product.is_synthetic is True
        assert product.actual_price is None, "Polarity files have no price; actual_price must be None"
        assert product.discounted_price is None, "Polarity files have no price; discounted_price must be None"
        assert product.discount_percentage is None, "discount_percentage must be None"

        # Check reviews
        assert len(reviews) == 2
        for r in reviews:
            assert r.user_id is None, "Polarity datasets have no user identity; user_id must be None"
            assert r.rating is None, "Polarity datasets have no star rating; rating must be None"
            assert r.source_polarity in ("positive", "negative"), "Polarity must be stored in source_polarity"
            assert r.review_id == _hash_review_content(r.review_title, r.review_content)

        # Users list must be empty (no fake 'Amazon Customer #N' / user_kag_N)
        assert len(users) == 0, "No fake user accounts should be synthesized"


@pytest.mark.anyio
async def test_products_list_and_kpis_never_include_unmatched_group_container(async_session: AsyncSession):
    """Assertion: list_products filters out kind='unmatched_group' so library and KPIs only include real products."""
    real_prod = Product(
        product_id="PROD-REAL-1",
        product_name="Real Wireless Earbuds",
        category="Electronics",
        kind="product",
        is_synthetic=False,
        actual_price=Decimal("2999.00"),
        discounted_price=Decimal("1999.00"),
    )
    container_prod = Product(
        product_id="UNMATCHED-JOB-1-BOOKS",
        product_name="Unmatched reviews - Books (import #1)",
        category="Books",
        kind="unmatched_group",
        is_synthetic=True,
    )
    async_session.add_all([real_prod, container_prod])
    await async_session.commit()

    # Query list_products with default kind="product"
    products = await list_products(async_session)
    product_ids = [p.product_id for p in products]

    assert "PROD-REAL-1" in product_ids, "Real products must be returned"
    assert "UNMATCHED-JOB-1-BOOKS" not in product_ids, "unmatched_group container must be filtered out"
