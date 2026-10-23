"""Idempotent DB writer for the harvester pipeline.

Design
------
All upserts use INSERT … ON CONFLICT DO NOTHING so that re-running the same
import is safe.  We commit after every product row so that a crash mid-run
leaves already-processed rows persisted and re-runs can pick up where they
left off (duplicates are silently skipped).

The ``run_csv_import`` coroutine is the public entry-point used by the API
route.  It mutates the ``CollectionJob`` passed in and returns it after
completion.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection_job import CollectionJob
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
)
from app.services.harvester.csv_adapter import CsvAmazonAdapter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Low-level upsert helpers (dialect-aware INSERT … ON CONFLICT DO NOTHING)
# ---------------------------------------------------------------------------


def _get_upsert_stmt(
    session: AsyncSession, model, values: dict, index_elements: list[str]
):
    dialect_name = getattr(getattr(session, "bind", None), "dialect", None)
    dialect_str = getattr(dialect_name, "name", "") if dialect_name else ""
    if dialect_str == "sqlite":
        from sqlalchemy.dialects.sqlite import insert as sqlite_insert

        return (
            sqlite_insert(model)
            .values(**values)
            .on_conflict_do_nothing(index_elements=index_elements)
        )
    from sqlalchemy.dialects.postgresql import insert as pg_insert

    return (
        pg_insert(model)
        .values(**values)
        .on_conflict_do_nothing(index_elements=index_elements)
    )


async def upsert_product(session: AsyncSession, p: NormalizedProduct) -> bool:
    """Insert product if product_id is new.  Returns True if inserted."""
    values = {
        "product_id": p.product_id,
        "product_name": p.product_name,
        "category": p.category,
        "discounted_price": p.discounted_price,
        "actual_price": p.actual_price,
        "discount_percentage": p.discount_percentage,
        "rating": p.rating,
        "rating_count": p.rating_count,
        "about_product": p.about_product,
        "img_link": p.img_link,
        "product_link": p.product_link,
    }
    stmt = _get_upsert_stmt(session, Product, values, ["product_id"])
    result = await session.execute(stmt)
    return bool(result.rowcount)


async def upsert_user(session: AsyncSession, u: NormalizedUser) -> bool:
    """Insert user if user_id is new.  Returns True if inserted."""
    values = {
        "user_id": u.user_id,
        "user_name": u.user_name,
    }
    stmt = _get_upsert_stmt(session, User, values, ["user_id"])
    result = await session.execute(stmt)
    return bool(result.rowcount)


async def upsert_review(session: AsyncSession, r: NormalizedReview) -> bool:
    """Insert review if review_id is new.  Returns True if inserted."""
    values = {
        "review_id": r.review_id,
        "product_id": r.product_id,
        "user_id": r.user_id,
        "rating": r.rating,
        "review_title": r.review_title,
        "review_content": r.review_content,
    }
    stmt = _get_upsert_stmt(session, Review, values, ["review_id"])
    result = await session.execute(stmt)
    return bool(result.rowcount)


# ---------------------------------------------------------------------------
# Public import entry-point
# ---------------------------------------------------------------------------


async def run_csv_import(
    session: AsyncSession,
    csv_path: str,
    job: CollectionJob,
    max_reviews: int | None = None,
) -> CollectionJob:
    """Import amazon.csv into the database; update *job* stats throughout.

    Parameters
    ----------
    session:
        An active async SQLAlchemy session.  The caller is responsible for
        adding *job* to the session before calling this function.
    csv_path:
        Absolute path to the Amazon review CSV file.
    job:
        A ``CollectionJob`` already persisted (or add-pending) in *session*.
        Its status, counts, and timestamps are mutated in place.
    max_reviews:
        Optional cap on total reviews to import. Useful for massive datasets.

    Returns
    -------
    The same *job* object with updated statistics.
    """
    job.status = "running"
    job.started_at = datetime.now(UTC)
    await session.flush()

    try:
        adapter = CsvAmazonAdapter(csv_path)
    except Exception as exc:  # noqa: BLE001
        job.status = "failed"
        job.finished_at = datetime.now(UTC)
        job.add_error(str(exc))
        await session.flush()
        return job

    for product, users, reviews in adapter.records():
        job.products_seen = (job.products_seen or 0) + 1

        # --- product -------------------------------------------------------
        try:
            inserted = await upsert_product(session, product)
            if inserted:
                job.products_inserted = (job.products_inserted or 0) + 1
                if product.discounted_price:
                    try:
                        from app.services.harvester.price_history import record_price_snapshot
                        await record_price_snapshot(
                            session=session,
                            product_id=product.product_id,
                            price=product.discounted_price,
                            original_price=product.actual_price,
                            currency="INR",
                            source="csv_import",
                        )
                    except Exception as exc:  # noqa: BLE001
                        logger.debug("harvester price_snapshot error=%s", exc)
        except Exception as exc:  # noqa: BLE001
            job.add_error(f"product {product.product_id}: {exc}")
            logger.warning("harvester product_id=%s error=%s", product.product_id, exc)
            await session.flush()
            continue

        # --- users ---------------------------------------------------------
        for user in users:
            try:
                await upsert_user(session, user)
            except Exception as exc:  # noqa: BLE001
                job.add_error(f"user {user.user_id}: {exc}")
                logger.debug("harvester user_id=%s error=%s", user.user_id, exc)

        # --- reviews -------------------------------------------------------
        for review in reviews:
            job.reviews_seen = (job.reviews_seen or 0) + 1
            try:
                inserted = await upsert_review(session, review)
                if inserted:
                    job.reviews_inserted = (job.reviews_inserted or 0) + 1
            except Exception as exc:  # noqa: BLE001
                job.add_error(f"review {review.review_id}: {exc}")
                logger.warning("harvester review_id=%s error=%s", review.review_id, exc)

        # Commit after each product row so progress is durable
        await session.commit()

        if max_reviews is not None and (job.reviews_seen or 0) >= max_reviews:
            logger.info("harvester reached max_reviews=%d, stopping import early", max_reviews)
            break

    job.status = "done"
    job.finished_at = datetime.now(UTC)
    await session.flush()
    await session.commit()

    logger.info(
        "harvester source=%s status=done products=%d reviews=%d errors=%d",
        job.source,
        job.products_inserted,
        job.reviews_inserted,
        job.error_count,
    )
    return job


# ---------------------------------------------------------------------------
# Helpers used by API routes (read-only queries)
# ---------------------------------------------------------------------------


async def get_job_by_id(session: AsyncSession, job_id: int) -> CollectionJob | None:
    result = await session.execute(
        select(CollectionJob).where(CollectionJob.id == job_id)
    )
    return result.scalar_one_or_none()


async def list_products(
    session: AsyncSession,
    limit: int = 20,
    offset: int = 0,
    category: str | None = None,
) -> list[Product]:
    stmt = select(Product)
    if category:
        stmt = stmt.where(Product.category.ilike(f"%{category}%"))
    stmt = stmt.order_by(Product.id.desc()).limit(limit).offset(offset)
    result = await session.execute(stmt)
    return list(result.scalars().all())


async def get_product_by_id(session: AsyncSession, product_id: str) -> Product | None:
    result = await session.execute(
        select(Product).where(Product.product_id == product_id)
    )
    return result.scalar_one_or_none()


async def list_reviews(
    session: AsyncSession,
    product_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Review]:
    query = select(Review).order_by(Review.id)
    if product_id:
        query = query.where(Review.product_id == product_id)
    result = await session.execute(query.limit(limit).offset(offset))
    return list(result.scalars().all())
