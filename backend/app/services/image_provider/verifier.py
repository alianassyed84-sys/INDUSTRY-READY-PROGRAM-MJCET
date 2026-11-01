"""Image URL verifier using async HEAD requests with timeout and in-memory caching."""

import asyncio
import logging
import urllib.error
import urllib.request

logger = logging.getLogger(__name__)

_VALID_IMAGE_MIMES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/avif",
    "image/gif",
    "image/svg+xml",
}


def _check_url_sync(url: str, timeout: float) -> bool:
    """Synchronous HEAD check with standard library urllib."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ReviewPulse/1.0 (ImageVerifier)"},
        method="HEAD",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get_content_type().lower()
            return resp.status in (200, 206) and (
                content_type in _VALID_IMAGE_MIMES or content_type.startswith("image/")
            )
    except urllib.error.HTTPError as err:
        if err.code == 405:  # Method Not Allowed -> fallback to small range GET
            try:
                get_req = urllib.request.Request(
                    url,
                    headers={
                        "User-Agent": "ReviewPulse/1.0 (ImageVerifier)",
                        "Range": "bytes=0-1024",
                    },
                    method="GET",
                )
                with urllib.request.urlopen(get_req, timeout=timeout) as get_resp:
                    content_type = get_resp.headers.get_content_type().lower()
                    return get_resp.status in (200, 206) and (
                        content_type in _VALID_IMAGE_MIMES or content_type.startswith("image/")
                    )
            except Exception:
                return False
        return False
    except Exception as exc:
        logger.warning("Image verification network error for %s: %s", url, exc)
        return False


class ImageVerifier:
    """Verifies that an image URL is reachable and serves real image content."""

    def __init__(self, timeout: float = 3.0) -> None:
        self._timeout = timeout
        self._cache: dict[str, bool] = {}

    async def verify(
        self,
        url: str | None,
        mock_status: int | None = None,
        mock_content_type: str | None = None,
    ) -> bool:
        """Verify image URL with HEAD request. Returns True if valid image content."""
        if not url or not url.strip():
            return False

        clean_url = url.strip()
        if clean_url in self._cache:
            return self._cache[clean_url]

        # Unit test mocking hook (zero network)
        if mock_status is not None:
            is_valid = mock_status in (200, 206) and bool(
                mock_content_type
                and (
                    mock_content_type.lower() in _VALID_IMAGE_MIMES
                    or mock_content_type.lower().startswith("image/")
                )
            )
            self._cache[clean_url] = is_valid
            return is_valid

        try:
            is_valid = await asyncio.to_thread(_check_url_sync, clean_url, self._timeout)
            self._cache[clean_url] = is_valid
            return is_valid
        except Exception as exc:
            logger.warning("Image verification failed for %s: %s", clean_url, exc)
            self._cache[clean_url] = False
            return False
