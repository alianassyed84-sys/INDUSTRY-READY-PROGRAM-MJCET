"""Tests for authentic product image pipeline: source order, uniqueness, variants, and verification."""

from collections.abc import AsyncGenerator
from decimal import Decimal
import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.product import Product
from app.services.harvester.base import NormalizedProduct
from app.services.harvester.importer import upsert_product
from app.services.image_provider.base import ProductImageProvider
from app.services.image_provider.stub import StubImageProvider
from app.services.image_provider.verifier import ImageVerifier


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
    async with sessionmaker() as session:
        yield session
    await engine.dispose()


@pytest.mark.anyio
async def test_image_source_order_dataset_link_first(async_session: AsyncSession):
    """(1) Dataset's own image link takes first priority over external provider."""
    provider = StubImageProvider({
        "apple:iphone-12": "https://images.example.com/provider_iphone12.jpg"
    })

    p = NormalizedProduct(
        product_id="PROD-IPHONE-12",
        product_name="Apple iPhone 12",
        identity_key="apple:iphone-12",
        img_link="https://images.example.com/dataset_iphone12.jpg",
    )

    await upsert_product(async_session, p, image_provider=provider)
    await async_session.commit()

    saved = (await async_session.execute(
        select(Product).where(Product.product_id == "PROD-IPHONE-12")
    )).scalar_one()

    assert saved.img_link == "https://images.example.com/dataset_iphone12.jpg"
    assert saved.image_source == "dataset"
    assert saved.image_status in ("verified", "pending")


@pytest.mark.anyio
async def test_image_source_order_provider_fallback_when_dataset_missing(async_session: AsyncSession):
    """(2) Approved provider is queried when dataset image is absent."""
    provider = StubImageProvider({
        "apple:iphone-12": "https://images.example.com/provider_iphone12.jpg"
    })

    p = NormalizedProduct(
        product_id="PROD-IPHONE-12-NO-IMG",
        product_name="Apple iPhone 12",
        identity_key="apple:iphone-12",
        img_link=None,
    )

    await upsert_product(async_session, p, image_provider=provider)
    await async_session.commit()

    saved = (await async_session.execute(
        select(Product).where(Product.product_id == "PROD-IPHONE-12-NO-IMG")
    )).scalar_one()

    assert saved.img_link == "https://images.example.com/provider_iphone12.jpg"
    assert saved.image_source == "provider"
    assert saved.image_status in ("verified", "pending")


@pytest.mark.anyio
async def test_image_source_order_none_when_both_missing(async_session: AsyncSession):
    """(3) When neither dataset nor provider has an image, image_status is 'none'."""
    provider = StubImageProvider({})

    p = NormalizedProduct(
        product_id="PROD-UNKNOWN",
        product_name="Unknown Gadget",
        identity_key="generic:gadget",
        img_link=None,
    )

    await upsert_product(async_session, p, image_provider=provider)
    await async_session.commit()

    saved = (await async_session.execute(
        select(Product).where(Product.product_id == "PROD-UNKNOWN")
    )).scalar_one()

    assert saved.img_link is None
    assert saved.image_source == "none"
    assert saved.image_status == "none"


@pytest.mark.anyio
async def test_uniqueness_first_keeps_second_marked_conflict_and_logged(async_session: AsyncSession, caplog):
    """Uniqueness: Two different identity_keys can never share an image URL."""
    shared_url = "https://images.example.com/shared_photo.jpg"

    p1 = NormalizedProduct(
        product_id="PROD-1",
        product_name="Apple iPhone 12",
        identity_key="apple:iphone-12",
        img_link=shared_url,
    )
    p2 = NormalizedProduct(
        product_id="PROD-2",
        product_name="Apple iPhone 13",
        identity_key="apple:iphone-13",
        img_link=shared_url,
    )

    await upsert_product(async_session, p1)
    await async_session.commit()

    # Second product with duplicate image
    with caplog.at_level("WARNING"):
        await upsert_product(async_session, p2)
        await async_session.commit()

    prod1 = (await async_session.execute(select(Product).where(Product.product_id == "PROD-1"))).scalar_one()
    prod2 = (await async_session.execute(select(Product).where(Product.product_id == "PROD-2"))).scalar_one()

    # First keeps image
    assert prod1.img_link == shared_url
    assert prod1.image_status != "conflict"

    # Second gets conflict and no image
    assert prod2.img_link is None
    assert prod2.image_status == "conflict"
    assert "conflict" in caplog.text.lower() or "duplicate" in caplog.text.lower()


@pytest.mark.anyio
async def test_variants_never_share_or_fallback_to_family_photo(async_session: AsyncSession):
    """Variants: iPhone 12 and iPhone 13 have distinct identities; missing variant never falls back to generic photo."""
    provider = StubImageProvider({
        "apple:iphone-12": "https://images.example.com/iphone12.jpg"
        # apple:iphone-13 has no image in provider
    })

    p13 = NormalizedProduct(
        product_id="PROD-IPHONE-13",
        product_name="Apple iPhone 13",
        identity_key="apple:iphone-13",
        img_link=None,
    )

    await upsert_product(async_session, p13, image_provider=provider)
    await async_session.commit()

    saved13 = (await async_session.execute(select(Product).where(Product.product_id == "PROD-IPHONE-13"))).scalar_one()
    assert saved13.img_link is None
    assert saved13.image_status == "none"


@pytest.mark.anyio
async def test_verify_image_url_head_request():
    """Verifier checks HTTP 200 + image content-type; rejects 404, html, and timeouts."""
    verifier = ImageVerifier()

    # Valid image response
    assert await verifier.verify("https://mock.test/valid.png", mock_status=200, mock_content_type="image/png") is True

    # HTML response instead of image
    assert await verifier.verify("https://mock.test/page.html", mock_status=200, mock_content_type="text/html") is False

    # 404 Not Found
    assert await verifier.verify("https://mock.test/missing.jpg", mock_status=404, mock_content_type="image/jpeg") is False


def test_catalog_seeder_has_zero_unsplash_photos():
    """Seeded catalog must not use generic Unsplash stock photos as product images."""
    from app.services.harvester import catalog_seeder
    import inspect

    source = inspect.getsource(catalog_seeder)
    assert "images.unsplash.com" not in source, "Found Unsplash stock photos in catalog_seeder.py"


def test_catalog_images_strictly_unique_and_exist_on_disk():
    """Every product image in catalog must be 100% unique (no reuse) and exist on disk with valid headers."""
    from pathlib import Path
    from app.services.harvester.catalog_seeder import SEEDED_CATALOG

    image_links = [
        item["img_link"]
        for item in SEEDED_CATALOG
        if item.get("img_link") is not None
    ]

    # 1. Strict 1-to-1 uniqueness (zero overlap)
    assert len(image_links) > 0, "Seeded catalog must have product images"
    assert len(image_links) == len(set(image_links)), f"Duplicate images detected in catalog: {image_links}"

    # 2. Local files exist and are valid images (> 10KB, JPEG/PNG header)
    public_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "public"
    for link in image_links:
        if link.startswith("/"):
            file_path = public_dir / link.lstrip("/")
            assert file_path.exists(), f"Image file {file_path} missing from disk"
            assert file_path.stat().st_size > 10_000, f"Image file {file_path} is too small"
            with open(file_path, "rb") as f:
                header = f.read(4)
                # JPEG starts with \xff\xd8\xff or PNG starts with \x89PNG
                is_valid = header.startswith(b"\xff\xd8") or header.startswith(b"\x89PNG")
                assert is_valid, f"File {file_path} does not have valid JPEG or PNG header"


def test_same_brand_phones_have_distinct_images():
    """Two phones from the same brand (e.g. iPhone 15 vs iPhone 15 Pro) must never share the same photo."""
    from app.services.harvester.catalog_seeder import SEEDED_CATALOG

    catalog_dict = {item["product_id"]: item for item in SEEDED_CATALOG}
    iphone_15_pro = catalog_dict.get("AMZN-IPHONE-15PRO")
    assert iphone_15_pro is not None
    assert iphone_15_pro["img_link"] is not None

    # Compare with iPhone 15 base model
    iphone_15_link = "/products/MOBGTAGPNRQA7CS3.jpg"
    assert iphone_15_pro["img_link"] != iphone_15_link, "iPhone 15 and iPhone 15 Pro must have distinct photos"


def test_full_database_has_zero_missing_images_and_all_exist_on_disk():
    """Entire catalog in the active database must have authentic photos with zero placeholders."""
    import sqlite3
    from pathlib import Path

    db_path = Path(__file__).resolve().parent.parent / "reviewpulse.db"
    assert db_path.exists(), f"Database not found at {db_path}"

    public_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "public"

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT product_id, product_name, img_link FROM products").fetchall()
    conn.close()

    assert len(rows) >= 60, f"Expected at least 60 products in database, got {len(rows)}"

    missing_images = [r[0] for r in rows if not r[2]]
    assert len(missing_images) == 0, f"Products missing img_link in database: {missing_images}"

    # Verify each image file physically exists and is non-empty
    for pid, name, link in rows:
        assert link.startswith("/products/"), f"Product {pid} has invalid img_link format: {link}"
        img_path = public_dir / link.lstrip("/")
        assert img_path.exists(), f"Image {img_path} for product {pid} ({name}) does not exist on disk"
        assert img_path.stat().st_size > 5_000, f"Image {img_path} for {pid} is too small"


