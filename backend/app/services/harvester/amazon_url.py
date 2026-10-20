"""Amazon.in product URL validation and ASIN extraction.

Provides pure, stdlib-only validation of consumer-submitted Amazon.in product URLs:
- Enforces HTTPS scheme.
- Restricts to explicitly authorized Amazon India domains.
- Forbids embedded authority credentials (phishing/deception prevention).
- Extracts and validates standard 10-character alphanumeric ASIN identifiers.
- Normalizes accepted URLs to canonical form (https://www.amazon.in/dp/{ASIN}).
- Does not perform network calls, scrape, or resolve HTTP redirects.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final
from urllib.parse import urlsplit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ALLOWED_HOSTNAMES: Final[frozenset[str]] = frozenset(
    {
        "amazon.in",
        "www.amazon.in",
        "m.amazon.in",
    }
)

_ASIN_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Z0-9]{10}$")

_CANONICAL_HOST: Final[str] = "www.amazon.in"


# ---------------------------------------------------------------------------
# Data contracts & Errors
# ---------------------------------------------------------------------------


class InvalidAmazonUrlError(ValueError):
    """Raised when a URL is not an acceptable or safe Amazon.in product URL."""


@dataclass(frozen=True)
class ValidatedAmazonUrl:
    """Normalized output contract for an approved Amazon.in product URL."""

    asin: str
    canonical_url: str
    raw_url: str
    hostname: str


# ---------------------------------------------------------------------------
# ASIN extraction & URL validation
# ---------------------------------------------------------------------------


def extract_asin_from_path(path: str) -> str | None:
    """Extract a 10-character candidate ASIN from recognized Amazon URL paths.

    Supported patterns:
      - /dp/{ASIN}
      - /gp/product/{ASIN}
      - /gp/aw/d/{ASIN}
      - /product/{ASIN}
      - /{product-slug}/dp/{ASIN}
      - /{product-slug}/gp/product/{ASIN}

    Returns None if no recognized product path pattern is found.
    """
    segments = [seg for seg in path.strip("/").split("/") if seg]
    num_segs = len(segments)

    for i, seg in enumerate(segments):
        # 1. /dp/{ASIN} or /.../dp/{ASIN}
        if seg == "dp" and i + 1 < num_segs:
            return segments[i + 1]

        # 2. /gp/product/{ASIN} or /.../gp/product/{ASIN}
        if seg == "gp" and i + 2 < num_segs and segments[i + 1] == "product":
            return segments[i + 2]

        # 3. /gp/aw/d/{ASIN} (mobile web app view)
        if (
            seg == "gp"
            and i + 3 < num_segs
            and segments[i + 1] == "aw"
            and segments[i + 2] == "d"
        ):
            return segments[i + 3]

        # 4. /product/{ASIN}
        if seg == "product" and i + 1 < num_segs:
            return segments[i + 1]

    return None


def validate_amazon_in_url(raw_url: str) -> ValidatedAmazonUrl:
    """Validate and normalize an Amazon.in product URL.

    Args:
        raw_url: Raw URL string provided by the caller.

    Returns:
        ValidatedAmazonUrl containing extracted ASIN and canonical URL.

    Raises:
        InvalidAmazonUrlError: On malformed, insecure, off-domain, or missing ASIN URLs.
    """
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise InvalidAmazonUrlError("URL cannot be empty or whitespace-only.")

    trimmed = raw_url.strip()

    try:
        parsed = urlsplit(trimmed)
    except Exception as exc:
        raise InvalidAmazonUrlError(f"Malformed URL: {exc}") from exc

    # 1. Scheme check: HTTPS only
    if parsed.scheme.lower() != "https":
        raise InvalidAmazonUrlError(
            f"Invalid scheme '{parsed.scheme}'. Only secure 'https' URLs are accepted."
        )

    # 2. Authority & Credentials check (reject embedded credentials)
    if parsed.username or parsed.password:
        raise InvalidAmazonUrlError(
            "URLs containing embedded credentials are forbidden."
        )

    # 3. Port check: Standard HTTPS (443 or default)
    if parsed.port is not None and parsed.port != 443:
        raise InvalidAmazonUrlError(
            f"Unsupported port {parsed.port}. Only default HTTPS (port 443) is allowed."
        )

    # 4. Hostname check: Strict whitelist for Amazon India
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        raise InvalidAmazonUrlError("URL is missing a valid hostname.")

    if hostname not in ALLOWED_HOSTNAMES:
        raise InvalidAmazonUrlError(
            f"Untrusted or unsupported hostname '{hostname}'. "
            f"Must be one of: {', '.join(sorted(ALLOWED_HOSTNAMES))}."
        )

    # 5. Extract ASIN from path (query parameters are explicitly not trusted for ID)
    candidate_asin = extract_asin_from_path(parsed.path)
    if candidate_asin is None:
        raise InvalidAmazonUrlError(
            "No recognized Amazon product identifier (/dp/, /gp/product/) "
            "found in URL path."
        )

    asin = candidate_asin.strip().upper()
    if not _ASIN_RE.match(asin):
        raise InvalidAmazonUrlError(
            f"Malformed ASIN '{candidate_asin}'. "
            "Expected a 10-character alphanumeric identifier."
        )

    canonical_url = f"https://{_CANONICAL_HOST}/dp/{asin}"

    return ValidatedAmazonUrl(
        asin=asin,
        canonical_url=canonical_url,
        raw_url=trimmed,
        hostname=hostname,
    )
