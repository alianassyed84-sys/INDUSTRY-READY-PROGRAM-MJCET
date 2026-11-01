"""Abstract base class for product image providers."""

from abc import ABC, abstractmethod


class ProductImageProvider(ABC):
    """Abstract interface for querying authentic product images by identity."""

    @abstractmethod
    async def fetch_product_image(self, identity_key: str, product_name: str) -> str | None:
        """Return an authentic, verified product image URL for the identity_key, or None.

        Must never return a stock or generic family image.
        """
