"""Product data provider abstraction for on-demand ASIN retrieval.

Provides:
- Explicit provider error hierarchy.
- Typed data contracts (ProviderProduct, ProviderReview).
- ProductDataProvider ABC.
- MockProductDataProvider for tests.
- DisabledProductDataProvider when live credentials are absent.
- Factory function get_product_provider(settings).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.config import Settings


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class ProviderError(Exception):
    """Base exception for all product data provider failures."""


class ProviderNotConfiguredError(ProviderError):
    """Raised when the requested provider is disabled or missing credentials."""


class ProviderAuthenticationError(ProviderError):
    """Raised when authentication credentials (API key, partner tag) fail."""


class ProductNotFoundError(ProviderError):
    """Raised when the specified ASIN does not exist in the provider catalog."""


class ProviderRateLimitError(ProviderError):
    """Raised when requests exceed the provider's rate limit or quota."""


class ProviderCommunicationError(ProviderError):
    """Raised when network, DNS, or upstream HTTP errors occur."""


# ---------------------------------------------------------------------------
# Data Contracts
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderReview:
    """A single review retrieved from a product provider."""

    review_id: str
    rating: float | None = None
    review_title: str | None = None
    review_content: str | None = None
    user_id: str | None = None
    user_name: str | None = None


@dataclass(frozen=True)
class ProviderProduct:
    """Product details and observed pricing retrieved from a provider."""

    asin: str
    title: str
    currency: str = "INR"
    current_price: float | None = None
    original_price: float | None = None
    discount_percentage: float | None = None
    rating: float | None = None
    rating_count: int | None = None
    category: str | None = None
    about_product: str | None = None
    img_url: str | None = None
    product_url: str | None = None
    reviews: tuple[ProviderReview, ...] = field(default_factory=tuple)
    source_name: str = "unknown"


# ---------------------------------------------------------------------------
# Interface & Implementations
# ---------------------------------------------------------------------------


class ProductDataProvider(ABC):
    """Abstract interface for external product data providers."""

    name: str = "base"

    @abstractmethod
    async def get_product_by_asin(self, asin: str) -> ProviderProduct | None:
        """Fetch product details for the specified ASIN.

        Returns None if product is not found, or raises a ProviderError subclass.
        """


class DisabledProductDataProvider(ProductDataProvider):
    """Default provider when no live or mock provider is enabled."""

    name: str = "disabled"

    def __init__(
        self, message: str = "No product data provider is configured."
    ) -> None:
        self.message = message

    async def get_product_by_asin(self, asin: str) -> ProviderProduct | None:
        raise ProviderNotConfiguredError(self.message)


class MockProductDataProvider(ProductDataProvider):
    """In-memory mock provider for deterministic tests."""

    name: str = "mock"

    def __init__(
        self,
        products: dict[str, ProviderProduct | Exception] | None = None,
        default_product: ProviderProduct | None = None,
    ) -> None:
        self.products: dict[str, ProviderProduct | Exception] = (
            dict(products) if products is not None else {}
        )
        self.default_product = default_product

    def add_product(self, product: ProviderProduct) -> None:
        self.products[product.asin] = product

    def set_error(self, asin: str, error: Exception) -> None:
        self.products[asin] = error

    async def get_product_by_asin(self, asin: str) -> ProviderProduct | None:
        if asin in self.products:
            entry = self.products[asin]
            if isinstance(entry, Exception):
                raise entry
            return entry

        if self.default_product is not None:
            return self.default_product

        return None


def get_product_provider(settings: Settings) -> ProductDataProvider:
    """Resolve and instantiate the configured product data provider."""
    provider_name = (settings.amazon_provider or "disabled").strip().lower()

    if provider_name == "mock":
        return MockProductDataProvider()

    if provider_name in {"creator_api", "pa_api", "amazon_creators"}:
        # Deferred to 6C: Check credentials and return provider or disabled stub
        from app.services.harvester.authorized_provider import (
            AmazonCreatorApiProvider,
        )

        return AmazonCreatorApiProvider(
            access_key=settings.amazon_access_key,
            secret_key=settings.amazon_secret_key,
            partner_tag=settings.amazon_partner_tag,
        )

    return DisabledProductDataProvider(
        f"Product provider '{provider_name}' is not enabled. Set "
        "AMAZON_PROVIDER=mock for tests or configure authorized provider credentials."
    )
