"""Tests for FlipkartReviewScraper service and Apify Actor data normalization."""

import pytest

from app.services.harvester.flipkart_scraper import (
    FlipkartReviewScraper,
    APIFY_RUN_START_COST_USD,
    APIFY_PER_REVIEW_COST_USD,
)
from app.services.harvester.flipkart_url import validate_flipkart_url


@pytest.mark.anyio
async def test_scraper_generates_valid_schema_in_mock_mode() -> None:
    url = "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm123?pid=MOBGTAGPNRQA7CS3"
    scraper = FlipkartReviewScraper(apify_token=None)

    result = await scraper.scrape(url, max_items=4, force_mock=True)

    assert result.is_mock is True
    assert result.product.product_id == "MOBGTAGPNRQA7CS3"
    assert "Apple Iphone 15" in result.product.product_name
    assert len(result.reviews) == 4
    assert len(result.raw_items) == 4
    assert len(result.users) > 0

    # Verify each raw review conforms to Actor schema fields
    for raw in result.raw_items:
        assert "reviewId" in raw
        assert "productId" in raw
        assert raw["productId"] == "MOBGTAGPNRQA7CS3"
        assert "title" in raw
        assert "text" in raw
        assert "rating" in raw
        assert 1.0 <= raw["rating"] <= 5.0
        assert "reviewer" in raw
        assert "certifiedBuyer" in raw
        assert "verifiedPurchase" in raw
        assert "helpfulCount" in raw
        assert "unhelpfulCount" in raw
        assert "variant" in raw
        assert isinstance(raw["variant"], list)

    # Cost calculation check
    expected_cost = round(APIFY_RUN_START_COST_USD + (4 * APIFY_PER_REVIEW_COST_USD), 6)
    assert result.estimated_cost_usd == expected_cost


@pytest.mark.anyio
async def test_scraper_normalizes_to_internal_contracts() -> None:
    validated = validate_flipkart_url(
        "https://www.flipkart.com/dell-xps-13/p/itm987?pid=COMGXYZ123456789"
    )
    scraper = FlipkartReviewScraper()
    result = await scraper.scrape(validated, max_items=2)

    # Internal NormalizedProduct
    assert result.product.product_id == "COMGXYZ123456789"
    assert result.product.category == "E-commerce (Flipkart)"
    assert result.product.rating is not None
    assert result.product.rating_count == 2

    # Internal NormalizedReviews
    for rev in result.reviews:
        assert rev.product_id == "COMGXYZ123456789"
        assert rev.review_id is not None
        assert rev.review_title is not None
        assert rev.review_content is not None
        assert rev.user_id is not None
        assert rev.user_id.startswith("fk_user_")

    # Internal NormalizedUsers
    for u in result.users:
        assert u.user_id.startswith("fk_user_")
        assert u.user_name != ""


@pytest.mark.anyio
async def test_scraper_bounds_inputs() -> None:
    url = "https://www.flipkart.com/p/itm?pid=TESTPID12345678"
    scraper = FlipkartReviewScraper()
    # bounds -10 to 1, bounds 9999 to 1000
    res1 = await scraper.scrape(url, max_items=-10)
    assert len(res1.reviews) >= 1
