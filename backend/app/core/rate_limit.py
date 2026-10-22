"""Configurable in-memory sliding-window rate limiting for FastAPI.

Provides deterministic request throttling with HTTP 429 and Retry-After headers.
Key resolution prioritizes authenticated user ID before falling back to remote IP.
Exempts health probes and provides test isolation hooks.
"""

from __future__ import annotations

import logging
import threading
import time
from collections import defaultdict
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, Request, Response, status

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _parse_rate_limit(rule: str) -> tuple[int, int]:
    """Parse limit strings like '60/minute' into (count, window_seconds)."""
    try:
        parts = rule.strip().lower().split("/")
        count = int(parts[0])
        unit = parts[1] if len(parts) > 1 else "minute"
        seconds_map = {
            "second": 1,
            "minute": 60,
            "hour": 3600,
            "day": 86400,
        }
        window = seconds_map.get(unit, 60)
        return count, window
    except Exception:
        return 60, 60


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding-window log rate limiter."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # key -> list of float timestamps
        self._history: dict[str, list[float]] = defaultdict(list)

    def check_and_record(
        self,
        key: str,
        max_requests: int,
        window_seconds: int,
    ) -> tuple[bool, int, int]:
        """Check if request is allowed under the rate limit.

        Returns:
            (allowed: bool, remaining: int, retry_after: int)
        """
        now = time.time()
        cutoff = now - window_seconds

        with self._lock:
            timestamps = self._history[key]
            # Prune timestamps outside current window
            pruned = [t for t in timestamps if t > cutoff]

            if len(pruned) >= max_requests:
                # Limit exceeded; calculate seconds until oldest request expires
                oldest = pruned[0]
                retry_after = max(1, int(oldest + window_seconds - now))
                self._history[key] = pruned
                return False, 0, retry_after

            # Allow request and record timestamp
            pruned.append(now)
            self._history[key] = pruned
            remaining = max(0, max_requests - len(pruned))
            return True, remaining, 0

    def reset(self) -> None:
        """Clear all rate limiting state (used between test cases)."""
        with self._lock:
            self._history.clear()


# Process-wide singleton rate limiter
_rate_limiter = SlidingWindowRateLimiter()


def get_rate_limiter() -> SlidingWindowRateLimiter:
    """Return the global rate limiter instance."""
    return _rate_limiter


def get_client_identifier(request: Request) -> str:
    """Derive rate-limiting key from request.

    Prefers verified user identity if present in request state;
    otherwise uses direct socket client IP to prevent spoofed X-Forwarded-For headers.
    """
    user = getattr(request.state, "user", None)
    if user and getattr(user, "user_id", None):
        return f"user:{user.user_id}"

    # Do not blindly trust X-Forwarded-For without trusted proxy middleware
    client_host = request.client.host if request.client else "unknown"
    return f"ip:{client_host}"


class RateLimitChecker:
    """FastAPI dependency for enforcing route-specific rate limits."""

    def __init__(
        self,
        limit_getter: Callable[[Settings], str],
        tier_name: str = "default",
    ) -> None:
        self.limit_getter = limit_getter
        self.tier_name = tier_name

    async def __call__(
        self,
        request: Request,
        response: Response,
        settings: Annotated[Settings, Depends(get_settings)],
    ) -> None:
        if not settings.rate_limit_enabled:
            return

        rule_str = self.limit_getter(settings)
        max_requests, window_seconds = _parse_rate_limit(rule_str)

        client_id = get_client_identifier(request)
        key = f"{self.tier_name}:{client_id}:{request.url.path}"

        allowed, remaining, retry_after = _rate_limiter.check_and_record(
            key=key,
            max_requests=max_requests,
            window_seconds=window_seconds,
        )

        response.headers["X-RateLimit-Limit"] = str(max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(window_seconds)

        if not allowed:
            response.headers["Retry-After"] = str(retry_after)
            logger.warning(
                "Rate limit exceeded tier=%s client=%s path=%s retry_after=%ds",
                self.tier_name,
                client_id,
                request.url.path,
                retry_after,
            )
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Rate limit exceeded for tier '{self.tier_name}'. "
                    f"Try again in {retry_after} seconds."
                ),
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(retry_after),
                },
            )


# Preconfigured dependencies for API routes
rate_limit_analysis = RateLimitChecker(
    lambda s: s.rate_limit_analysis, tier_name="analysis"
)
rate_limit_harvester = RateLimitChecker(
    lambda s: s.rate_limit_harvester, tier_name="harvester"
)
rate_limit_price_check = RateLimitChecker(
    lambda s: s.rate_limit_price_check, tier_name="price_check"
)
rate_limit_default = RateLimitChecker(
    lambda s: s.rate_limit_default, tier_name="default"
)
