"""Field normalization helpers for raw review-source data.

All functions are pure; they accept a raw string value (or None) and return
a typed Python value or ``None`` on failure.  They never raise.

Design
------
These helpers are deliberately kept simple and stdlib-only so that they are
fast enough to handle thousands of rows per second and are trivially testable
without mocking.
"""

from __future__ import annotations

import re
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

# ---------------------------------------------------------------------------
# Price
# ---------------------------------------------------------------------------

_PRICE_RE = re.compile(r"[^\d.]")
_TWO_PLACES = Decimal("0.01")


def parse_price(raw: str | None) -> Decimal | None:
    """Strip currency symbols, commas, and whitespace; return Decimal or None.

    Examples::

        parse_price("₹1,099")  -> Decimal("1099.00")
        parse_price("$19.99")  -> Decimal("19.99")
        parse_price("")        -> None
        parse_price(None)      -> None
    """
    if not raw or not raw.strip():
        return None
    cleaned = _PRICE_RE.sub("", raw.strip())
    if not cleaned:
        return None
    try:
        val = Decimal(cleaned)
        if not val.is_finite() or val < 0:
            return None
        return val.quantize(_TWO_PLACES, rounding=ROUND_HALF_UP)
    except (InvalidOperation, ValueError):
        return None


# ---------------------------------------------------------------------------
# Rating (0.0 – 5.0 expected for Amazon star ratings)
# ---------------------------------------------------------------------------

_RATING_MIN = 0.0
_RATING_MAX = 5.0


def parse_rating(raw: str | None) -> float | None:
    """Parse a rating string into a float; return None if missing or invalid.

    Examples::

        parse_rating("4.2")  -> 4.2
        parse_rating("|")    -> None   (row 1279 anomaly in amazon.csv)
        parse_rating("")     -> None
        parse_rating(None)   -> None
    """
    if not raw or not raw.strip():
        return None
    try:
        value = float(raw.strip())
    except ValueError:
        return None
    if value < _RATING_MIN or value > _RATING_MAX:
        return None
    return value


# ---------------------------------------------------------------------------
# Rating count
# ---------------------------------------------------------------------------


def parse_rating_count(raw: str | None) -> int | None:
    """Strip commas and parse to int; return None if missing or invalid.

    Examples::

        parse_rating_count("24,269")  -> 24269
        parse_rating_count("")        -> None
    """
    if not raw or not raw.strip():
        return None
    cleaned = raw.strip().replace(",", "")
    try:
        return int(cleaned)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Percentage
# ---------------------------------------------------------------------------


def parse_percentage(raw: str | None) -> float | None:
    """Strip trailing ``%`` and parse to float; return None if invalid.

    Examples::

        parse_percentage("64%")  -> 64.0
        parse_percentage("")     -> None
    """
    if not raw or not raw.strip():
        return None
    cleaned = raw.strip().rstrip("%")
    try:
        return float(cleaned)
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------------------------


def clean_text(raw: str | None, max_len: int | None = None) -> str | None:
    """Strip leading/trailing whitespace; return None for empty strings.

    Optionally truncates to *max_len* characters (no mid-word cut warning
    needed — this is for safety only, not display).
    """
    if not raw:
        return None
    text = raw.strip()
    if not text:
        return None
    if max_len and len(text) > max_len:
        text = text[:max_len]
    return text
