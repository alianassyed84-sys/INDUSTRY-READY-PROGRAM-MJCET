"""Flipkart product reviews scraper service integrating Apify Actor.

Actor: automation-lab/flipkart-product-reviews-scraper
Exports individual public Flipkart product reviews with text, ratings,
reviewer names, displayed dates, variant attributes, purchase flags and helpful votes.

Supports:
- Live API calls via Apify REST API using httpx.AsyncClient when APIFY_TOKEN is set.
- Deterministic high-fidelity fallback generator when APIFY_TOKEN is absent or in tests.
- Maps raw Apify dataset items to NormalizedProduct, NormalizedUser, and NormalizedReview.
- Computes estimated pay-per-event Apify billing costs.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import urllib.error
import urllib.request
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
)
from app.services.harvester.flipkart_url import (
    ValidatedFlipkartUrl,
    validate_flipkart_url,
)
from app.services.harvester.provider import (
    ProviderAuthenticationError,
    ProviderCommunicationError,
    ProviderError,
    ProviderRateLimitError,
)

logger = logging.getLogger(__name__)

APIFY_ACTOR_ID = "automation-lab~flipkart-product-reviews-scraper"
APIFY_BASE_URL = "https://api.apify.com/v2"

# Cost rates from Apify Actor specs:
# Pay per event: $0.0005 per started run
# FREE tier item rate: $0.0018308 per exported review
APIFY_RUN_START_COST_USD = 0.0005
APIFY_PER_REVIEW_COST_USD = 0.0018308


@dataclass(frozen=True)
class FlipkartScraperResult:
    """Structured result from a Flipkart scraping run."""

    product: NormalizedProduct
    users: list[NormalizedUser]
    reviews: list[NormalizedReview]
    raw_items: list[dict[str, Any]]
    estimated_cost_usd: float
    is_mock: bool
    status_note: str


class FlipkartReviewScraper:
    """Service client for the Apify Flipkart Product Reviews Scraper Actor."""

    def __init__(
        self,
        apify_token: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> None:
        self.apify_token = (apify_token or "").strip()
        self.timeout_seconds = timeout_seconds

    async def scrape(
        self,
        url: str | ValidatedFlipkartUrl,
        max_items: int = 25,
        max_pages_per_product: int = 3,
        force_mock: bool = False,
    ) -> FlipkartScraperResult:
        """Scrape Flipkart product reviews using Apify Actor or fallback generator."""
        validated = (
            url if isinstance(url, ValidatedFlipkartUrl) else validate_flipkart_url(url)
        )
        bounded_items = max(1, min(max_items, 1000))
        bounded_pages = max(1, min(max_pages_per_product, 100))

        if self.apify_token and not force_mock:
            try:
                raw_items = await self._run_apify_live(
                    target_url=validated.canonical_url,
                    max_items=bounded_items,
                    max_pages_per_product=bounded_pages,
                )
                is_mock = False
            except ProviderError as exc:
                logger.warning(
                    "Apify live run failed (%s); falling back to mock provider", exc
                )
                raw_items = self._generate_mock_items(
                    validated=validated, max_items=bounded_items
                )
                is_mock = True
        else:
            raw_items = self._generate_mock_items(
                validated=validated, max_items=bounded_items
            )
            is_mock = True

        return self._normalize_dataset(
            validated=validated, raw_items=raw_items, is_mock=is_mock
        )

    def _http_request_sync(
        self,
        url: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> tuple[int, Any]:
        """Perform a synchronous HTTP request using Python standard library."""
        req_headers = dict(headers or {})
        data_bytes = None
        if json_data is not None:
            data_bytes = json.dumps(json_data).encode("utf-8")
            req_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            url=url,
            data=data_bytes,
            headers=req_headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as resp:
                status = resp.status
                body = resp.read().decode("utf-8")
                return status, json.loads(body) if body else None
        except urllib.error.HTTPError as err:
            body = err.read().decode("utf-8") if err.fp else ""
            try:
                parsed = json.loads(body)
            except Exception:
                parsed = None
            return err.code, parsed
        except urllib.error.URLError as err:
            raise ProviderCommunicationError(f"Apify network error: {err.reason}") from err
        except TimeoutError as err:
            raise ProviderCommunicationError(f"Apify request timed out: {err}") from err

    async def _run_apify_live(
        self,
        target_url: str,
        max_items: int,
        max_pages_per_product: int,
    ) -> list[dict[str, Any]]:
        """Call Apify Actor via REST API and return default dataset items."""
        headers = {
            "Authorization": f"Bearer {self.apify_token}",
            "Accept": "application/json",
        }
        actor_input = {
            "startUrls": [{"url": target_url}],
            "maxItems": max_items,
            "maxPagesPerProduct": max_pages_per_product,
        }

        # Try sync execution endpoint: /run-sync-get-dataset-items
        sync_url = f"{APIFY_BASE_URL}/acts/{APIFY_ACTOR_ID}/run-sync-get-dataset-items?timeout={int(self.timeout_seconds)}"

        status, data = await asyncio.to_thread(
            self._http_request_sync,
            url=sync_url,
            method="POST",
            headers=headers,
            json_data=actor_input,
        )

        if status == 200:
            if isinstance(data, list):
                return data
            if isinstance(data, dict) and "items" in data:
                return data["items"]

        if status in (401, 403):
            raise ProviderAuthenticationError(
                f"Apify authentication failed (HTTP {status})"
            )
        if status == 429:
            raise ProviderRateLimitError("Apify rate limit or quota exceeded")

        # Fallback to standard start-and-poll run if sync endpoint returns non-200
        return await self._run_apify_async_poll(headers, actor_input)

    async def _run_apify_async_poll(
        self,
        headers: dict[str, str],
        actor_input: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Start Actor run and retrieve dataset items upon completion."""
        start_url = f"{APIFY_BASE_URL}/acts/{APIFY_ACTOR_ID}/runs?waitForFinish=45"
        status, resp_data = await asyncio.to_thread(
            self._http_request_sync,
            url=start_url,
            method="POST",
            headers=headers,
            json_data=actor_input,
        )

        if status not in (200, 201) or not isinstance(resp_data, dict):
            raise ProviderError(f"Failed to start Apify Actor run: HTTP {status}")

        run_data = resp_data.get("data", {})
        dataset_id = run_data.get("defaultDatasetId")
        if not dataset_id:
            raise ProviderError("No defaultDatasetId returned by Apify run")

        # Fetch items from dataset
        dataset_url = f"{APIFY_BASE_URL}/datasets/{dataset_id}/items"
        d_status, items = await asyncio.to_thread(
            self._http_request_sync,
            url=dataset_url,
            method="GET",
            headers=headers,
        )
        if d_status != 200:
            raise ProviderError(f"Failed to fetch dataset items: HTTP {d_status}")
        return items if isinstance(items, list) else []

    def _generate_mock_items(
        self,
        validated: ValidatedFlipkartUrl,
        max_items: int,
    ) -> list[dict[str, Any]]:
        """Generate realistic mock review items conforming to the Apify Actor schema."""
        pid = validated.pid
        title_hint = validated.title_hint or "Premium Electronics Device"
        mock_templates = [
            (
                "Superb product, worth every penny!",
                "Excellent battery backup, crisp display and very responsive touch. Highly recommended for daily use.",
                5.0,
                "Rajesh Kumar",
                "May, 2024",
                142,
                12,
                [{"name": "Color", "value": "Midnight Black"}, {"name": "Storage", "value": "128 GB"}],
            ),
            (
                "Great camera but slightly warm during fast charging",
                "The build quality is premium and photo clarity is top notch in daylight. Only issue is slight heating when charging quickly.",
                4.0,
                "Sneha Sharma",
                "Apr, 2024",
                98,
                7,
                [{"name": "Color", "value": "Midnight Black"}, {"name": "Storage", "value": "128 GB"}],
            ),
            (
                "Value for money deal!",
                "Got this during Flipkart Big Billion Days. Unbeatable price to performance ratio with certified warranty.",
                5.0,
                "Amit Patel",
                "Mar, 2024",
                210,
                15,
                [{"name": "Color", "value": "Starlight Blue"}, {"name": "Storage", "value": "256 GB"}],
            ),
            (
                "Decent performance, battery could be better",
                "Average sound quality and standard battery life. Good for general browsing and streaming, but heavy gaming drains it fast.",
                3.0,
                "Pooja Verma",
                "Feb, 2024",
                45,
                23,
                [{"name": "Color", "value": "Silver"}, {"name": "Storage", "value": "128 GB"}],
            ),
            (
                "Exceptional build and seamless user experience",
                "Switching from my older model was effortless. Software animations are butter smooth and camera low-light modes surprised me.",
                5.0,
                "Vikram Singh",
                "Jan, 2024",
                312,
                19,
                [{"name": "Color", "value": "Midnight Black"}, {"name": "Storage", "value": "256 GB"}],
            ),
            (
                "Not satisfied with delivery packaging",
                "The outer box had dents upon arrival. The device itself works fine, but seller needs to improve bubble wrap packaging.",
                3.0,
                "Kavita Reddy",
                "Dec, 2023",
                18,
                34,
                [{"name": "Color", "value": "Midnight Black"}, {"name": "Storage", "value": "128 GB"}],
            ),
        ]

        items: list[dict[str, Any]] = []
        for i in range(min(max_items, len(mock_templates))):
            tmpl = mock_templates[i]
            review_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{pid}-review-{i}"))
            items.append(
                {
                    "reviewId": review_uuid,
                    "reviewUrl": f"{validated.canonical_url}#review-{review_uuid}",
                    "productId": pid,
                    "reviewProductId": pid,
                    "title": tmpl[0],
                    "text": tmpl[1],
                    "rating": tmpl[2],
                    "reviewer": tmpl[3],
                    "displayedDate": tmpl[4],
                    "certifiedBuyer": True,
                    "verifiedPurchase": True,
                    "helpfulCount": tmpl[5],
                    "unhelpfulCount": tmpl[6],
                    "variant": tmpl[7],
                    "sourceUrl": validated.canonical_url,
                    "scrapedAt": "2024-05-01T12:00:00Z",
                }
            )

        return items

    def _normalize_dataset(
        self,
        validated: ValidatedFlipkartUrl,
        raw_items: list[dict[str, Any]],
        is_mock: bool,
    ) -> FlipkartScraperResult:
        """Convert Apify raw items into internal models."""
        pid = validated.pid
        product_name = validated.title_hint or f"Flipkart Product {pid}"

        ratings: list[float] = []
        users: list[NormalizedUser] = []
        reviews: list[NormalizedReview] = []

        seen_users: set[str] = set()

        for item in raw_items:
            rev_id = str(item.get("reviewId") or uuid.uuid4())
            rating_val = item.get("rating")
            try:
                rating_float = float(rating_val) if rating_val is not None else None
            except (ValueError, TypeError):
                rating_float = None

            if rating_float is not None:
                ratings.append(rating_float)

            reviewer_name = str(item.get("reviewer") or "Flipkart Customer").strip()
            # Deterministic user id based on reviewer name
            user_id = f"fk_user_{hashlib.sha256(reviewer_name.encode('utf-8')).hexdigest()[:12]}"

            if user_id not in seen_users:
                seen_users.add(user_id)
                users.append(NormalizedUser(user_id=user_id, user_name=reviewer_name))

            title = item.get("title")
            text = item.get("text") or ""

            reviews.append(
                NormalizedReview(
                    review_id=rev_id,
                    product_id=pid,
                    user_id=user_id,
                    rating=rating_float,
                    review_title=str(title) if title else None,
                    review_content=str(text),
                )
            )

        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None
        rating_count = len(ratings)

        product = NormalizedProduct(
            product_id=pid,
            product_name=product_name,
            category="E-commerce (Flipkart)",
            discounted_price=Decimal("19999.00") if is_mock else None,
            actual_price=Decimal("24999.00") if is_mock else None,
            discount_percentage=20.0 if is_mock else None,
            rating=avg_rating,
            rating_count=rating_count,
            about_product=(
                f"Flipkart product {pid}. Exported via Apify Actor "
                "automation-lab/flipkart-product-reviews-scraper."
            ),
            img_link=None,
            product_link=validated.canonical_url,
        )

        estimated_cost = round(
            APIFY_RUN_START_COST_USD + (len(raw_items) * APIFY_PER_REVIEW_COST_USD), 6
        )
        provider_mode = "Mock Simulation" if is_mock else "Apify Cloud Actor"
        status_note = (
            f"Successfully ingested {len(reviews)} reviews via {provider_mode} "
            f"(Est. cost: ${estimated_cost:.5f} USD)."
        )

        return FlipkartScraperResult(
            product=product,
            users=users,
            reviews=reviews,
            raw_items=raw_items,
            estimated_cost_usd=estimated_cost,
            is_mock=is_mock,
            status_note=status_note,
        )
