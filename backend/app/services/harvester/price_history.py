"""Price history recording and analytics based strictly on observed snapshots.

Guarantees:
- Never fabricates historical data.
- Highest/lowest prices calculated exclusively from persisted PriceSnapshot rows.
- A single observation is treated as a baseline, never as an established peak.
- Prevents misleading cross-currency comparisons by scoping price math to matching
  currency.
- Protects against duplicate snapshot insertion.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import desc, select

from app.models.price_snapshot import PriceSnapshot

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models.product import Product
    from app.services.harvester.provider import ProductDataProvider


@dataclass(frozen=True)
class PriceSnapshotItem:
    """A single recorded price point."""

    price: float
    original_price: float | None
    currency: str
    source: str
    observed_at: datetime


@dataclass(frozen=True)
class PriceHistorySummary:
    """Analytical summary of recorded price snapshots."""

    product_id: str
    observations_count: int
    first_observed_price: float | None
    latest_observed_price: float | None
    current_price: float | None
    highest_observed_price: float | None
    lowest_observed_price: float | None
    price_change_amount: float | None
    price_change_percentage: float | None
    currency: str
    is_multi_currency: bool
    tracking_start: datetime | None
    tracking_end: datetime | None
    tracking_period_days: float
    is_historical_peak: bool
    status_note: str
    snapshots: tuple[PriceSnapshotItem, ...]


async def record_price_snapshot(
    session: AsyncSession,
    product_id: str,
    price: float,
    original_price: float | None = None,
    currency: str = "INR",
    source: str = "unknown",
    deduplicate: bool = True,
) -> PriceSnapshot:
    """Persist a new price observation with validation and deduplication."""
    if not isinstance(price, (int, float)) or price <= 0 or not math.isfinite(price):
        raise ValueError("Price must be a positive, finite number.")

    clean_curr = (currency or "INR").strip().upper()
    if not clean_curr:
        raise ValueError("Currency cannot be empty.")

    clean_src = (source or "unknown").strip()

    if deduplicate:
        # Check most recent snapshot to avoid duplicate sequential recordings
        latest_stmt = (
            select(PriceSnapshot)
            .where(PriceSnapshot.product_id == product_id)
            .order_by(desc(PriceSnapshot.observed_at))
            .limit(1)
        )
        last_snap = (await session.execute(latest_stmt)).scalar_one_or_none()
        if (
            last_snap is not None
            and last_snap.price == float(price)
            and last_snap.original_price == original_price
            and last_snap.currency == clean_curr
            and last_snap.source == clean_src
        ):
            return last_snap

    snapshot = PriceSnapshot(
        product_id=product_id,
        price=float(price),
        original_price=float(original_price) if original_price is not None else None,
        currency=clean_curr,
        source=clean_src,
    )
    session.add(snapshot)
    await session.flush()
    return snapshot


async def get_price_history(
    session: AsyncSession,
    product_id: str,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    limit: int = 100,
    offset: int = 0,
) -> PriceHistorySummary:
    """Retrieve and compute price analytics from persisted snapshots.

    Validates date filtering and ensures multi-currency data is not combined
    into misleading comparisons.
    """
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start_date cannot be after end_date.")

    query = select(PriceSnapshot).where(PriceSnapshot.product_id == product_id)

    if start_date is not None:
        query = query.where(PriceSnapshot.observed_at >= start_date)
    if end_date is not None:
        query = query.where(PriceSnapshot.observed_at <= end_date)

    query = query.order_by(PriceSnapshot.observed_at.asc())
    result = await session.execute(query)
    records = list(result.scalars().all())

    if not records:
        return PriceHistorySummary(
            product_id=product_id,
            observations_count=0,
            first_observed_price=None,
            latest_observed_price=None,
            current_price=None,
            highest_observed_price=None,
            lowest_observed_price=None,
            price_change_amount=None,
            price_change_percentage=None,
            currency="INR",
            is_multi_currency=False,
            tracking_start=None,
            tracking_end=None,
            tracking_period_days=0.0,
            is_historical_peak=False,
            status_note="No price snapshots recorded for this product.",
            snapshots=(),
        )

    # Multi-currency guard: do not mix currencies in price math
    currencies = sorted({r.currency for r in records if r.currency})
    is_multi_currency = len(currencies) > 1
    primary_currency = records[-1].currency or "INR"

    if is_multi_currency:
        calc_records = [r for r in records if r.currency == primary_currency]
        curr_note = (
            f"Multi-currency observations detected ({', '.join(currencies)}). "
            f"Comparison metrics strictly calculated for {primary_currency}."
        )
    else:
        calc_records = records
        curr_note = ""

    first_price = calc_records[0].price
    latest_price = calc_records[-1].price
    highest_price = max(r.price for r in calc_records)
    lowest_price = min(r.price for r in calc_records)
    change_amount = round(latest_price - first_price, 2)
    change_pct = (
        round(((latest_price - first_price) / first_price) * 100, 2)
        if first_price > 0
        else 0.0
    )

    tracking_start = records[0].observed_at
    tracking_end = records[-1].observed_at
    period_days = 0.0
    if tracking_start and tracking_end:
        period_days = round(
            max((tracking_end - tracking_start).total_seconds() / 86400, 0.0), 2
        )

    count = len(calc_records)
    if count == 1:
        is_peak = False
        base_note = (
            "Single price observation recorded within period; insufficient "
            "history to establish a historical peak (treated as baseline, "
            "not a confirmed historical peak)."
        )
    else:
        is_peak = bool(latest_price >= highest_price)
        base_note = (
            f"Calculated strictly from {count} recorded price snapshots in "
            f"{primary_currency}."
        )

    status_note = f"{base_note} {curr_note}".strip()

    # Paginate snapshots
    paged = records[offset : offset + limit] if limit > 0 else records[offset:]
    items = tuple(
        PriceSnapshotItem(
            price=r.price,
            original_price=r.original_price,
            currency=r.currency,
            source=r.source,
            observed_at=r.observed_at,
        )
        for r in paged
    )

    return PriceHistorySummary(
        product_id=product_id,
        observations_count=len(records),
        first_observed_price=first_price,
        latest_observed_price=latest_price,
        current_price=latest_price,
        highest_observed_price=highest_price,
        lowest_observed_price=lowest_price,
        price_change_amount=change_amount,
        price_change_percentage=change_pct,
        currency=primary_currency,
        is_multi_currency=is_multi_currency,
        tracking_start=tracking_start,
        tracking_end=tracking_end,
        tracking_period_days=period_days,
        is_historical_peak=is_peak,
        status_note=status_note,
        snapshots=items,
    )


async def poll_product_price(
    session: AsyncSession,
    product: Product,
    provider: ProductDataProvider,
) -> PriceSnapshot | None:
    """Fetch current price from configured provider and record a snapshot if changed."""
    provider_data = await provider.get_product_by_asin(product.product_id)
    if provider_data is None or provider_data.current_price is None:
        return None

    snapshot = await record_price_snapshot(
        session=session,
        product_id=product.product_id,
        price=provider_data.current_price,
        original_price=provider_data.original_price,
        currency=provider_data.currency,
        source=provider_data.source_name,
        deduplicate=True,
    )
    await session.commit()
    return snapshot
