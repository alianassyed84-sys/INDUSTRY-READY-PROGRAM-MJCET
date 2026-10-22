"""Harvester source adapter interface.

Any future review source (e.g. Amazon Product Advertising API, RSS feed,
authenticated partner dataset) MUST subclass SourceAdapter and implement
``records()``.  The CSV adapter is the only concrete implementation shipped
with Milestone 3; all others are out of scope until credentials / authorisation
are available.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal

# ---------------------------------------------------------------------------
# Normalised data contracts
# ---------------------------------------------------------------------------


@dataclass
class NormalizedProduct:
    """A product in the canonical internal format."""

    product_id: str
    product_name: str
    category: str | None = None
    discounted_price: Decimal | None = None
    actual_price: Decimal | None = None
    discount_percentage: float | None = None
    rating: float | None = None
    rating_count: int | None = None
    about_product: str | None = None
    img_link: str | None = None
    product_link: str | None = None


@dataclass
class NormalizedUser:
    """A reviewer in the canonical internal format."""

    user_id: str
    user_name: str = "Anonymous"


@dataclass
class NormalizedReview:
    """A single review in the canonical internal format."""

    review_id: str
    product_id: str
    user_id: str | None = None
    rating: float | None = None
    review_title: str | None = None
    review_content: str | None = None


# ---------------------------------------------------------------------------
# Source adapter ABC
# ---------------------------------------------------------------------------

#: Tuple emitted by each call to :py:meth:`SourceAdapter.records`.
RecordTuple = tuple[NormalizedProduct, list[NormalizedUser], list[NormalizedReview]]


class SourceAdapter(ABC):
    """Abstract base class for all review source adapters.

    Implementation contract
    -----------------------
    Subclasses MUST:

    1. Set a unique ``source_id`` class attribute (used as the *source* field in
       :class:`~app.models.collection_job.CollectionJob`).
    2. Implement :py:meth:`records` as a generator that yields ``RecordTuple``
       values — one per logical *product row* in the source.

    Subclasses SHOULD:

    - Raise ``SourceNotConfiguredError`` in ``__init__`` when required credentials
      or files are absent, so callers can detect the issue before starting a job.
    - Be stateless between calls to ``records()`` so that re-running a job is safe.

    Example stub for a future API adapter::

        class AmazonPaApiAdapter(SourceAdapter):
            source_id = "amazon_pa_api"

            def __init__(self, api_key: str, api_secret: str, partner_tag: str) -> None:
                if not api_key:
                    raise SourceNotConfiguredError("AMAZON_PA_API_KEY is required")
                self._api_key = api_key
                ...

            def records(self) -> Iterator[RecordTuple]:
                # Fetch from live API (credentials required)
                raise NotImplementedError
    """

    source_id: str = ""

    @abstractmethod
    def records(self) -> Iterator[RecordTuple]:
        """Yield ``(product, users, reviews)`` tuples from the source."""


class SourceNotConfiguredError(RuntimeError):
    """Raised when a source adapter is missing required credentials or files."""
