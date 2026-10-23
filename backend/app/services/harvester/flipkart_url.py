"""Flipkart product URL validation and PID extraction.

Pure stdlib-only validation of Flipkart product URLs:
- Enforces HTTPS scheme.
- Restricts to explicitly authorized Flipkart domains (flipkart.com, www.flipkart.com, dl.flipkart.com).
- Forbids embedded authority credentials (phishing/deception prevention).
- Extracts and validates standard Flipkart Product Identifier (PID) from query parameter.
- Normalizes accepted URLs to canonical form with PID.
- Extracts optional title hint from product slug for catalog creation.
- Does not perform network calls or scrape in validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final
from urllib.parse import parse_qs, urlsplit

ALLOWED_FLIPKART_HOSTNAMES: Final[frozenset[str]] = frozenset(
    {
        "flipkart.com",
        "www.flipkart.com",
        "dl.flipkart.com",
    }
)

_PID_RE: Final[re.Pattern[str]] = re.compile(r"^[A-Za-z0-9_]{6,32}$")
_CANONICAL_FLIPKART_HOST: Final[str] = "www.flipkart.com"


class InvalidFlipkartUrlError(ValueError):
    """Raised when a URL is not an acceptable or safe Flipkart product URL."""


@dataclass(frozen=True)
class ValidatedFlipkartUrl:
    """Normalized output contract for an approved Flipkart product URL."""

    pid: str
    canonical_url: str
    raw_url: str
    hostname: str
    title_hint: str | None = None


def extract_title_hint_from_path(path: str) -> str | None:
    """Extract a human-readable title hint from Flipkart slug if available."""
    segments = [seg for seg in path.strip("/").split("/") if seg]
    if not segments:
        return None

    # Handle /product-reviews/{slug}/... or /{slug}/p/...
    slug = None
    if segments[0] == "product-reviews" and len(segments) > 1:
        slug = segments[1]
    elif segments[0] == "dl" and len(segments) > 1:
        slug = segments[1]
    elif segments[0] not in {"p", "account", "checkout", "search"}:
        slug = segments[0]

    if slug and slug not in {"p", "product-reviews"}:
        # replace dashes with spaces and title case
        words = [w for w in re.split(r"[-_]+", slug) if w]
        if words:
            return " ".join(words).title()
    return None


def validate_flipkart_url(raw_url: str) -> ValidatedFlipkartUrl:
    """Validate and normalize a Flipkart product or reviews URL.

    Args:
        raw_url: Raw URL string provided by caller.

    Returns:
        ValidatedFlipkartUrl with extracted PID, canonical URL, and title hint.

    Raises:
        InvalidFlipkartUrlError: On malformed, insecure, off-domain, or missing PID URLs.
    """
    if not isinstance(raw_url, str) or not raw_url.strip():
        raise InvalidFlipkartUrlError("URL cannot be empty or whitespace-only.")

    trimmed = raw_url.strip()

    try:
        parsed = urlsplit(trimmed)
    except Exception as exc:
        raise InvalidFlipkartUrlError(f"Malformed URL: {exc}") from exc

    # 1. Scheme check: HTTPS only
    if parsed.scheme.lower() != "https":
        raise InvalidFlipkartUrlError(
            f"Invalid scheme '{parsed.scheme}'. Only secure 'https' URLs are accepted."
        )

    # 2. Authority & Credentials check
    if parsed.username or parsed.password:
        raise InvalidFlipkartUrlError(
            "URLs containing embedded credentials are forbidden."
        )

    # 3. Port check: Standard HTTPS (443 or default)
    if parsed.port is not None and parsed.port != 443:
        raise InvalidFlipkartUrlError(
            f"Unsupported port {parsed.port}. Only default HTTPS (port 443) is allowed."
        )

    # 4. Hostname check
    hostname = (parsed.hostname or "").lower().rstrip(".")
    if not hostname:
        raise InvalidFlipkartUrlError("URL is missing a valid hostname.")

    if hostname not in ALLOWED_FLIPKART_HOSTNAMES:
        raise InvalidFlipkartUrlError(
            f"Untrusted or unsupported hostname '{hostname}'. "
            f"Must be one of: {', '.join(sorted(ALLOWED_FLIPKART_HOSTNAMES))}."
        )

    # 5. Extract and validate 'pid' from query parameters
    query_params = parse_qs(parsed.query, keep_blank_values=False)
    pids = query_params.get("pid")
    if not pids or not pids[0].strip():
        raise InvalidFlipkartUrlError(
            "Missing 'pid' query parameter in Flipkart URL. "
            "A full product URL with '?pid=...' is required."
        )

    pid = pids[0].strip().upper()
    if not _PID_RE.match(pid):
        raise InvalidFlipkartUrlError(
            f"Malformed Flipkart PID '{pids[0]}'. Expected 6-32 alphanumeric characters."
        )

    title_hint = extract_title_hint_from_path(parsed.path)
    canonical_url = f"https://{_CANONICAL_FLIPKART_HOST}{parsed.path}?pid={pid}"

    return ValidatedFlipkartUrl(
        pid=pid,
        canonical_url=canonical_url,
        raw_url=trimmed,
        hostname=hostname,
        title_hint=title_hint,
    )
