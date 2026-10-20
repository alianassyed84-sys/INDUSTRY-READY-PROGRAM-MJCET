"""Harvester service package.

Public API:
    run_csv_import  — import amazon.csv into the database
    SourceAdapter   — ABC for future review sources
    NormalizedProduct, NormalizedUser, NormalizedReview — shared data contracts
    validate_amazon_in_url — validate Amazon India product URLs
    ProductDataProvider — interface for live/mock product providers
    get_price_history — compute observed price statistics
"""

from app.services.harvester.amazon_url import (
    InvalidAmazonUrlError,
    ValidatedAmazonUrl,
    validate_amazon_in_url,
)
from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
    SourceAdapter,
)
from app.services.harvester.importer import run_csv_import
from app.services.harvester.insights import compute_product_insights
from app.services.harvester.price_history import (
    get_price_history,
    poll_product_price,
    record_price_snapshot,
)
from app.services.harvester.provider import (
    DisabledProductDataProvider,
    MockProductDataProvider,
    ProductDataProvider,
    ProductNotFoundError,
    ProviderAuthenticationError,
    ProviderCommunicationError,
    ProviderError,
    ProviderNotConfiguredError,
    ProviderProduct,
    ProviderRateLimitError,
    ProviderReview,
    get_product_provider,
)

__all__ = [
    "DisabledProductDataProvider",
    "InvalidAmazonUrlError",
    "MockProductDataProvider",
    "NormalizedProduct",
    "NormalizedReview",
    "NormalizedUser",
    "ProductDataProvider",
    "ProductNotFoundError",
    "ProviderAuthenticationError",
    "ProviderCommunicationError",
    "ProviderError",
    "ProviderNotConfiguredError",
    "ProviderProduct",
    "ProviderRateLimitError",
    "ProviderReview",
    "SourceAdapter",
    "ValidatedAmazonUrl",
    "compute_product_insights",
    "get_price_history",
    "get_product_provider",
    "poll_product_price",
    "record_price_snapshot",
    "run_csv_import",
    "validate_amazon_in_url",
]
