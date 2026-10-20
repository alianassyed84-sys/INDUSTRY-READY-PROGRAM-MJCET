"""Price history recording and analytics based strictly on observed snapshots.

Guarantees:
- Never fabricates historical data.
- Highest/lowest prices calculated exclusively from persisted PriceSnapshot rows.
- A single observation is treated as a baseline, never as an established peak.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from app.models.price_snapshot import PriceSnapshot

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


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
    current_price: float | None
    highest_observed_price: float | None
    lowest_observed_price: float | None
    currency: str
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
) -> PriceSnapshot:
    """Persist a new price observation for a product."""
    snapshot = PriceSnapshot(
        product_id=product_id,
        price=price,
        original_price=original_price,
        currency=currency,
        source=source,
    )
    session.add(snapshot)
    await session.flush()
    return snapshot


async def get_price_history(
    session: AsyncSession,
    product_id: str,
) -> PriceHistorySummary:
    """Retrieve and compute price analytics from persisted snapshots.

    Does not fabricate historical data. If 0 or 1 snapshots exist, historical
    peaks are marked uncertain.
    """
    stmt = (
        select(PriceSnapshot)
        .where(PriceSnapshot.product_id == product_id)
        .order_by(PriceSnapshot.observed_at.asc())
    )
    result = await session.execute(stmt)
    records = list(result.scalars().all())

    if not records:
        return PriceHistorySummary(
            product_id=product_id,
            observations_count=0,
            current_price=None,
            highest_observed_price=None,
            lowest_observed_price=None,
            currency="INR",
            is_historical_peak=False,
            status_note="No price snapshots recorded for this product.",
            snapshots=(),
        )

    prices = [r.price for r in records if r.price is not None]
    highest = max(prices) if prices else None
    lowest = min(prices) if prices else None
    latest = records[-1].price
    currency = records[-1].currency

    count = len(records)
    if count == 1:
        is_peak = False
        note = (
            "Single price observation recorded; insufficient history to "
            "establish a historical peak."
        )
    else:
        is_peak = bool(latest is not None and highest is not None and latest >= highest)
        note = f"Calculated strictly from {count} recorded price snapshots."

    items = tuple(
        PriceSnapshotItem(
            price=r.price,
            original_price=r.original_price,
            currency=r.currency,
            source=r.source,
            observed_at=r.observed_at,
        )
        for r in records
    )

    return PriceHistorySummary(
        product_id=product_id,
        observations_count=count,
        current_price=latest,
        highest_observed_price=highest,
        lowest_observed_price=lowest,
        currency=currency,
        is_historical_peak=is_peak,
        status_note=note,
        snapshots=items,
    )
