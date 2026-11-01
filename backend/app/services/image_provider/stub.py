"""Deterministic stub image provider for tests and offline operations."""

from app.services.image_provider.base import ProductImageProvider


class StubImageProvider(ProductImageProvider):
    """Local, offline stub provider that maps exact identity keys to image URLs."""

    def __init__(self, mapping: dict[str, str] | None = None) -> None:
        self._mapping = mapping or {}

    async def fetch_product_image(self, identity_key: str, product_name: str) -> str | None:
        # Strict exact match by identity_key — never fall back to generic or family photos
        return self._mapping.get(identity_key)
