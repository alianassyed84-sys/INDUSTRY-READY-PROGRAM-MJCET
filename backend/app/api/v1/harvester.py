"""Harvester API endpoints.

Routes
------
POST /api/v1/harvester/jobs                  — start an import job (runs synchronously)
GET  /api/v1/harvester/jobs/{job_id}         — fetch job status by ID
GET  /api/v1/harvester/products              — paginated product list
GET  /api/v1/harvester/products/{product_id} — product detail
GET  /api/v1/harvester/reviews               — paginated review list

Design notes
------------
- All DB-backed routes return 503 when DATABASE_URL is not configured.
- The import job runs synchronously inside the request handler (no background
  queue). For the 1,465-row CSV this takes ~1-3 s.  A task queue is deferred
  to a future milestone.
- Pagination uses ?limit (max 100) and ?offset query parameters.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import AuthenticatedUser, get_current_user, require_admin
from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.rate_limit import (
    rate_limit_default,
    rate_limit_harvester,
    rate_limit_price_check,
)
from app.models.collection_job import CollectionJob
from app.schemas.harvester import (
    AnalyzeUrlRequest,
    FlipkartReviewItem,
    FlipkartScrapeRequest,
    FlipkartScrapeResponse,
    JobStartRequest,
    JobStatusResponse,
    PaginatedProducts,
    PaginatedReviews,
    PriceHistoryResponse,
    PriceSnapshotSchema,
    ProductComparisonResponse,
    ProductDetailResponse,
    ProductInsightsResponse,
    ProductUrlAnalysisResponse,
)
from app.services.harvester.amazon_url import (
    InvalidAmazonUrlError,
    validate_amazon_in_url,
)
from app.services.harvester.comparator import compare_product_platforms
from app.services.harvester.flipkart_scraper import (
    FlipkartReviewScraper,
)
from app.services.harvester.flipkart_url import (
    InvalidFlipkartUrlError,
    validate_flipkart_url,
)
from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
)
from app.services.harvester.importer import (
    get_job_by_id,
    get_product_by_id,
    list_products,
    list_reviews,
    run_csv_import,
    upsert_product,
    upsert_review,
    upsert_user,
)
from app.services.harvester.insights import compute_product_insights
from app.services.harvester.price_history import (
    PriceHistorySummary,
    get_price_history,
    poll_product_price,
    record_price_snapshot,
)
from app.services.harvester.provider import (
    ProductNotFoundError,
    ProviderAuthenticationError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderRateLimitError,
    get_product_provider,
)

router = APIRouter()
logger = logging.getLogger(__name__)

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbDep = Annotated[AsyncSession | None, Depends(get_db)]
CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]
AdminUserDep = Annotated[AuthenticatedUser, Depends(require_admin)]

# ponytail: cap pagination to avoid accidental full-table dumps
_MAX_LIMIT = 100


def _require_db(settings: Settings) -> None:
    """Raise 503 if DATABASE_URL is not configured."""
    if not settings.database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is not configured. Set DATABASE_URL.",
        )


# ---------------------------------------------------------------------------
# Job management
# ---------------------------------------------------------------------------


@router.post(
    "/jobs",
    response_model=JobStatusResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start a review import job",
    description=(
        "Starts an import job for the specified source and runs it synchronously "
        "(completes before responding). Requires administrative privileges. "
        "Source CSV path is determined strictly by server configuration."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_harvester)],
)
async def start_job(
    payload: JobStartRequest,
    settings: SettingsDep,
    db: DbDep,
    _admin: AdminUserDep,
) -> JobStatusResponse:
    """Create a CollectionJob, run the import, and return the final status."""
    _require_db(settings)
    assert db is not None

    csv_path = settings.amazon_csv_path
    if not csv_path or not (os.path.isfile(csv_path) or os.path.isdir(csv_path)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Dataset source is not configured or unavailable on the server.",
        )

    job = CollectionJob(source=payload.source, status="pending")
    db.add(job)
    await db.flush()  # get the auto-generated id

    logger.info("harvester job_id=%d source=%s start", job.id, job.source)
    await run_csv_import(
        session=db,
        csv_path=csv_path,
        job=job,
        max_reviews=payload.max_reviews or settings.amazon_import_limit,
    )

    return JobStatusResponse(**job.to_dict())


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get collection job status",
    tags=["harvester"],
    dependencies=[Depends(rate_limit_harvester)],
)
async def get_job(
    job_id: int,
    settings: SettingsDep,
    db: DbDep,
    _admin: AdminUserDep,
) -> JobStatusResponse:
    """Retrieve the status and statistics of a collection job by ID."""
    _require_db(settings)
    assert db is not None

    job = await get_job_by_id(db, job_id)
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found.",
        )
    return JobStatusResponse(**job.to_dict())


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------


@router.get(
    "/products",
    response_model=PaginatedProducts,
    summary="List imported products",
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_products(
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
    limit: int = Query(20, ge=1, le=_MAX_LIMIT),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None, description="Optional category filter"),
) -> PaginatedProducts:
    """Return a paginated list of products stored in the database."""
    _require_db(settings)
    assert db is not None

    products = await list_products(db, limit=limit, offset=offset, category=category)
    items = [
        {
            "product_id": p.product_id,
            "product_name": p.product_name,
            "category": p.category,
            "rating": p.rating,
            "rating_count": p.rating_count,
            "discounted_price": p.discounted_price,
            "actual_price": p.actual_price,
            "discount_percentage": p.discount_percentage,
            "img_link": p.img_link,
        }
        for p in products
    ]
    return PaginatedProducts(
        total_returned=len(items),
        limit=limit,
        offset=offset,
        items=items,  # type: ignore[arg-type]
    )


@router.get(
    "/products/{product_id}/compare",
    response_model=ProductComparisonResponse,
    summary="Compare Amazon and Flipkart reviews and intelligence for a product",
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_product_comparison(
    product_id: str,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
) -> ProductComparisonResponse:
    """Return side-by-side review intelligence comparing Amazon and Flipkart."""
    _require_db(settings)
    assert db is not None

    comparison = await compare_product_platforms(session=db, product_id=product_id)
    if comparison is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )
    return comparison


@router.get(
    "/products/{product_id}",
    response_model=ProductDetailResponse,
    summary="Get product detail",
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_product(
    product_id: str,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
) -> ProductDetailResponse:
    """Return full product detail including about text and links."""
    _require_db(settings)
    assert db is not None

    product = await get_product_by_id(db, product_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )
    return ProductDetailResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        category=product.category,
        rating=product.rating,
        rating_count=product.rating_count,
        discounted_price=product.discounted_price,
        actual_price=product.actual_price,
        discount_percentage=product.discount_percentage,
        about_product=product.about_product,
        img_link=product.img_link,
        product_link=product.product_link,
        created_at=product.created_at,
    )


@router.get(
    "/products/{product_id}/insights",
    response_model=ProductInsightsResponse,
    summary="Get aggregated product intelligence and review analytics",
    description=(
        "Computes on-demand sentiment distribution, top TF-IDF topics, "
        "rating statistics, and readability metrics for all reviews of a product. "
        "Optionally extracts aspect-targeted polarity via the 'aspects' parameter."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_product_insights(
    product_id: str,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
    limit: int = Query(100, ge=1, le=500, description="Max reviews to analyze"),
    aspects: str | None = Query(
        None,
        description=(
            "Comma-separated list of target aspects to evaluate "
            "(e.g. 'quality,battery,price')"
        ),
    ),
) -> ProductInsightsResponse:
    """Return aggregated review intelligence for a product."""
    _require_db(settings)
    assert db is not None

    parsed_aspects = (
        [a.strip() for a in aspects.split(",") if a.strip()]
        if aspects is not None
        else None
    )

    insights = await compute_product_insights(
        session=db,
        product_id=product_id,
        limit=limit,
        aspects=parsed_aspects,
    )
    if insights is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{product_id}' not found.",
        )
    return insights


def _build_price_history_response(
    history: PriceHistorySummary,
) -> PriceHistoryResponse:
    return PriceHistoryResponse(
        product_id=history.product_id,
        observations_count=history.observations_count,
        first_observed_price=history.first_observed_price,
        latest_observed_price=history.latest_observed_price,
        current_price=history.current_price,
        highest_observed_price=history.highest_observed_price,
        lowest_observed_price=history.lowest_observed_price,
        price_change_amount=history.price_change_amount,
        price_change_percentage=history.price_change_percentage,
        currency=history.currency,
        is_multi_currency=history.is_multi_currency,
        tracking_start=history.tracking_start,
        tracking_end=history.tracking_end,
        tracking_period_days=history.tracking_period_days,
        is_historical_peak=history.is_historical_peak,
        status_note=history.status_note,
        snapshots=[
            PriceSnapshotSchema(
                price=s.price,
                original_price=s.original_price,
                currency=s.currency,
                source=s.source,
                observed_at=s.observed_at,
            )
            for s in history.snapshots
        ],
    )


@router.get(
    "/products/{product_id}/price-history",
    response_model=PriceHistoryResponse,
    summary="Get chronological price history and analytics for a product",
    description=(
        "Retrieves recorded price snapshots, tracking period, first/latest "
        "observed price, min/max observed prices, price change amount and "
        "percentage, and multi-currency guards."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_product_price_history(
    product_id: str,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
    start_date: Annotated[
        datetime | None,
        Query(description="Filter snapshots observed on or after this timestamp"),
    ] = None,
    end_date: Annotated[
        datetime | None,
        Query(description="Filter snapshots observed on or before this timestamp"),
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=500, description="Max snapshots to return"),
    ] = 100,
    offset: Annotated[
        int,
        Query(ge=0, description="Pagination offset"),
    ] = 0,
) -> PriceHistoryResponse:
    """Retrieve chronological price history and summary metrics for a product."""
    _require_db(settings)
    assert db is not None

    clean_id = (product_id or "").strip()
    product = await get_product_by_id(db, clean_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{clean_id}' not found.",
        )

    try:
        history = await get_price_history(
            session=db,
            product_id=clean_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc

    return _build_price_history_response(history)


@router.post(
    "/products/{product_id}/check-price",
    response_model=PriceHistoryResponse,
    summary="Poll configured provider for a fresh price observation",
    description=(
        "Queries the active provider for current product pricing, records "
        "a new snapshot if valid, and returns updated price history statistics."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_price_check)],
)
async def check_product_price(
    product_id: str,
    settings: SettingsDep,
    db: DbDep,
    _admin: AdminUserDep,
) -> PriceHistoryResponse:
    """Poll the configured provider for current price and record a snapshot."""
    _require_db(settings)
    assert db is not None

    clean_id = (product_id or "").strip()
    product = await get_product_by_id(db, clean_id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{clean_id}' not found.",
        )

    provider = get_product_provider(settings)
    try:
        await poll_product_price(session=db, product=product, provider=provider)
    except ProviderNotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Provider is not configured: {exc}",
        ) from exc
    except ProviderAuthenticationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider authentication failed: {exc}",
        ) from exc
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product '{clean_id}' not found by provider: {exc}",
        ) from exc
    except ProviderRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Provider rate limit exceeded: {exc}",
        ) from exc
    except ProviderError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Provider error: {exc}",
        ) from exc

    history = await get_price_history(session=db, product_id=clean_id)
    return _build_price_history_response(history)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


@router.get(
    "/reviews",
    response_model=PaginatedReviews,
    summary="List imported reviews",
    tags=["harvester"],
    dependencies=[Depends(rate_limit_default)],
)
async def get_reviews(
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
    product_id: str | None = Query(None, description="Filter reviews by product_id"),
    limit: int = Query(20, ge=1, le=_MAX_LIMIT),
    offset: int = Query(0, ge=0),
) -> PaginatedReviews:
    """Return a paginated list of reviews, optionally filtered by product."""
    _require_db(settings)
    assert db is not None

    reviews = await list_reviews(db, product_id=product_id, limit=limit, offset=offset)
    items = [
        {
            "review_id": r.review_id,
            "product_id": r.product_id,
            "user_id": r.user_id,
            "rating": r.rating,
            "review_title": r.review_title,
            "review_content": r.review_content,
            "created_at": r.created_at,
        }
        for r in reviews
    ]
    return PaginatedReviews(
        total_returned=len(items),
        limit=limit,
        offset=offset,
        items=items,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# On-Demand URL Analysis
# ---------------------------------------------------------------------------


@router.post(
    "/analyze-url",
    response_model=ProductUrlAnalysisResponse,
    summary="Validate and analyze Amazon.in product URL",
    description=(
        "Validates an Amazon.in or Flipkart product URL, retrieves product metadata "
        "from database or configured provider, persists price snapshots, "
        "and computes NLP review insights."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_harvester)],
)
async def analyze_url(
    payload: AnalyzeUrlRequest,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
) -> ProductUrlAnalysisResponse:
    """Analyze an Amazon.in or Flipkart product URL on-demand."""
    _require_db(settings)
    assert db is not None

    url_str = payload.url.strip()
    is_flipkart = "flipkart.com" in url_str.lower()

    if is_flipkart:
        try:
            fk_validated = validate_flipkart_url(url_str)
        except InvalidFlipkartUrlError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Invalid Flipkart URL: {exc}",
            ) from exc

        pid = fk_validated.pid
        product = await get_product_by_id(db, pid)

        if product is None:
            scraper = FlipkartReviewScraper(apify_token=settings.apify_token)
            try:
                fk_result = await scraper.scrape(fk_validated, max_items=25)
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Flipkart review scraping error: {exc}",
                ) from exc

            await upsert_product(db, fk_result.product)
            for u in fk_result.users:
                await upsert_user(db, u)
            for r in fk_result.reviews:
                await upsert_review(db, r)

            if fk_result.product.discounted_price is not None:
                await record_price_snapshot(
                    db,
                    product_id=pid,
                    price=fk_result.product.discounted_price,
                    original_price=fk_result.product.actual_price,
                    currency="INR",
                    source="flipkart_scraper",
                )

            await db.commit()
            product = await get_product_by_id(db, pid)

        assert product is not None

        history_check = await get_price_history(db, pid)
        if history_check.observations_count == 0 and product.discounted_price is not None:
            await record_price_snapshot(
                db,
                product_id=product.product_id,
                price=product.discounted_price,
                original_price=product.actual_price,
                currency="INR",
                source="catalog_baseline",
            )
            await db.commit()
            history_check = await get_price_history(db, pid)

        insights = await compute_product_insights(session=db, product_id=pid, limit=100)
        status_note = (
            f"Flipkart product resolved with {insights.total_reviews_analyzed if insights else 0} review(s) analyzed."
        )

        product_detail = ProductDetailResponse(
            product_id=product.product_id,
            product_name=product.product_name,
            category=product.category,
            rating=product.rating,
            rating_count=product.rating_count,
            discounted_price=product.discounted_price,
            actual_price=product.actual_price,
            discount_percentage=product.discount_percentage,
            about_product=product.about_product,
            img_link=product.img_link,
            product_link=product.product_link,
            created_at=product.created_at,
        )

        return ProductUrlAnalysisResponse(
            asin=pid,
            canonical_url=fk_validated.canonical_url,
            product=product_detail,
            price_history=_build_price_history_response(history_check),
            insights=insights,
            status_note=status_note,
        )

    # Standard Amazon.in flow
    try:
        validated = validate_amazon_in_url(payload.url)
    except InvalidAmazonUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid Amazon.in URL: {exc}",
        ) from exc

    asin = validated.asin
    product = await get_product_by_id(db, asin)

    if product is None:
        provider = get_product_provider(settings)
        try:
            provider_data = await provider.get_product_by_asin(asin)
        except ProviderNotConfiguredError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"Product '{asin}' is not in database and provider is "
                    f"not configured: {exc}"
                ),
            ) from exc
        except ProviderAuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Provider authentication failed: {exc}",
            ) from exc
        except ProductNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{asin}' not found by provider: {exc}",
            ) from exc
        except ProviderRateLimitError as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Provider rate limit exceeded: {exc}",
            ) from exc
        except ProviderError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Provider error: {exc}",
            ) from exc

        if provider_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product '{asin}' was not found.",
            )

        norm_product = NormalizedProduct(
            product_id=provider_data.asin,
            product_name=provider_data.title,
            category=provider_data.category,
            discounted_price=provider_data.current_price,
            actual_price=provider_data.original_price,
            discount_percentage=provider_data.discount_percentage,
            rating=provider_data.rating,
            rating_count=provider_data.rating_count,
            about_product=provider_data.about_product,
            img_link=provider_data.img_url,
            product_link=provider_data.product_url or validated.canonical_url,
        )
        await upsert_product(db, norm_product)

        for rev in provider_data.reviews:
            if rev.user_id:
                await upsert_user(
                    db,
                    NormalizedUser(
                        user_id=rev.user_id,
                        user_name=rev.user_name or "Anonymous",
                    ),
                )
            await upsert_review(
                db,
                NormalizedReview(
                    review_id=rev.review_id,
                    product_id=provider_data.asin,
                    user_id=rev.user_id,
                    rating=rev.rating,
                    review_title=rev.review_title,
                    review_content=rev.review_content,
                ),
            )

        if provider_data.current_price is not None:
            await record_price_snapshot(
                db,
                product_id=provider_data.asin,
                price=provider_data.current_price,
                original_price=provider_data.original_price,
                currency=provider_data.currency,
                source=provider_data.source_name,
            )

        await db.commit()
        product = await get_product_by_id(db, asin)

    assert product is not None

    # Record baseline snapshot from product catalog if no snapshots exist yet
    history_check = await get_price_history(db, asin)
    if history_check.observations_count == 0 and product.discounted_price is not None:
        await record_price_snapshot(
            db,
            product_id=product.product_id,
            price=product.discounted_price,
            original_price=product.actual_price,
            currency="INR",
            source="catalog_baseline",
        )
        await db.commit()
        history_check = await get_price_history(db, asin)

    insights = await compute_product_insights(session=db, product_id=asin, limit=100)

    if insights is None or insights.total_reviews_analyzed == 0:
        status_note = "Product resolved; no review text available for NLP analysis."
    else:
        status_note = (
            f"Analysis complete based on {insights.total_reviews_analyzed} review(s)."
        )

    product_detail = ProductDetailResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        category=product.category,
        rating=product.rating,
        rating_count=product.rating_count,
        discounted_price=product.discounted_price,
        actual_price=product.actual_price,
        discount_percentage=product.discount_percentage,
        about_product=product.about_product,
        img_link=product.img_link,
        product_link=product.product_link,
        created_at=product.created_at,
    )

    price_history_resp = _build_price_history_response(history_check)

    return ProductUrlAnalysisResponse(
        asin=asin,
        canonical_url=validated.canonical_url,
        product=product_detail,
        price_history=price_history_resp,
        insights=insights,
        status_note=status_note,
    )


# ---------------------------------------------------------------------------
# Dedicated Flipkart Review Scraper (Apify Actor)
# ---------------------------------------------------------------------------


@router.post(
    "/flipkart/scrape",
    response_model=FlipkartScrapeResponse,
    summary="Scrape Flipkart product reviews using Apify Actor",
    description=(
        "Executes Apify Actor 'automation-lab/flipkart-product-reviews-scraper' "
        "to export individual public product reviews, stores them in ReviewPulse database, "
        "and computes NLP sentiment intelligence."
    ),
    tags=["harvester"],
    dependencies=[Depends(rate_limit_harvester)],
)
async def scrape_flipkart(
    payload: FlipkartScrapeRequest,
    settings: SettingsDep,
    db: DbDep,
    _user: CurrentUserDep,
) -> FlipkartScrapeResponse:
    """Scrape and store public Flipkart product reviews via Apify Actor."""
    _require_db(settings)
    assert db is not None

    try:
        validated = validate_flipkart_url(payload.url)
    except InvalidFlipkartUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Invalid Flipkart URL: {exc}",
        ) from exc

    scraper = FlipkartReviewScraper(
        apify_token=settings.apify_token,
        timeout_seconds=60.0,
    )
    try:
        result = await scraper.scrape(
            url=validated,
            max_items=payload.max_items,
            max_pages_per_product=payload.max_pages_per_product,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Flipkart reviews scraper error: {exc}",
        ) from exc

    await upsert_product(db, result.product)
    for u in result.users:
        await upsert_user(db, u)
    for r in result.reviews:
        await upsert_review(db, r)

    if result.product.discounted_price is not None:
        await record_price_snapshot(
            db,
            product_id=result.product.product_id,
            price=result.product.discounted_price,
            original_price=result.product.actual_price,
            currency="INR",
            source="flipkart_scraper",
        )

    await db.commit()
    persisted_product = await get_product_by_id(db, result.product.product_id)
    assert persisted_product is not None

    insights = await compute_product_insights(
        session=db,
        product_id=result.product.product_id,
        limit=100,
    )

    review_items: list[FlipkartReviewItem] = []
    for item in result.raw_items:
        try:
            review_items.append(FlipkartReviewItem.model_validate(item))
        except Exception:
            pass

    product_detail = ProductDetailResponse(
        product_id=persisted_product.product_id,
        product_name=persisted_product.product_name,
        category=persisted_product.category,
        rating=persisted_product.rating,
        rating_count=persisted_product.rating_count,
        discounted_price=persisted_product.discounted_price,
        actual_price=persisted_product.actual_price,
        discount_percentage=persisted_product.discount_percentage,
        about_product=persisted_product.about_product,
        img_link=persisted_product.img_link,
        product_link=persisted_product.product_link,
        created_at=persisted_product.created_at,
    )

    return FlipkartScrapeResponse(
        product_id=result.product.product_id,
        product_name=result.product.product_name,
        canonical_url=validated.canonical_url,
        reviews_count=len(result.reviews),
        estimated_cost_usd=result.estimated_cost_usd,
        is_mock_provider=result.is_mock,
        product=product_detail,
        reviews=review_items,
        insights=insights,
        status_note=result.status_note,
    )

