"""Pydantic schemas for the Review Harvester endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Job management
# ---------------------------------------------------------------------------


class JobStartRequest(BaseModel):
    """Payload for starting a new collection job."""

    model_config = ConfigDict(extra="forbid")

    source: Literal["csv_amazon"] = Field(
        "csv_amazon",
        description=(
            "Review source identifier.  Currently only 'csv_amazon' is supported "
            "(the bundled Amazon product review CSV dataset)."
        ),
    )
    csv_path: str | None = Field(
        None,
        description=(
            "Absolute path to the Amazon CSV file.  "
            "Defaults to the AMAZON_CSV_PATH setting when omitted."
        ),
    )


class JobStatusResponse(BaseModel):
    """Status snapshot for a single collection job."""

    model_config = ConfigDict(extra="forbid")

    id: int
    source: str
    status: str = Field(
        ...,
        description="pending | running | done | failed",
    )
    products_seen: int = Field(0, ge=0)
    products_inserted: int = Field(0, ge=0)
    products_skipped: int = Field(0, ge=0)
    reviews_seen: int = Field(0, ge=0)
    reviews_inserted: int = Field(0, ge=0)
    reviews_skipped: int = Field(0, ge=0)
    warning_count: int = Field(0, ge=0)
    error_count: int = Field(0, ge=0)
    error_sample: list[str] = Field(
        default_factory=list,
        description="Up to 10 error messages sampled during the run.",
    )
    started_at: datetime | None = None
    finished_at: datetime | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Product list / detail
# ---------------------------------------------------------------------------


class ProductListItem(BaseModel):
    """Compact product record for paginated listings."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    category: str | None = None
    rating: float | None = None
    rating_count: int | None = None
    discounted_price: float | None = None
    actual_price: float | None = None
    discount_percentage: float | None = None


class ProductDetailResponse(ProductListItem):
    """Full product record including about text and links."""

    about_product: str | None = None
    img_link: str | None = None
    product_link: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Review list
# ---------------------------------------------------------------------------


class ReviewListItem(BaseModel):
    """A single review record."""

    model_config = ConfigDict(extra="forbid")

    review_id: str
    product_id: str
    user_id: str | None = None
    rating: float | None = None
    review_title: str | None = None
    review_content: str | None = None
    created_at: datetime | None = None


# ---------------------------------------------------------------------------
# Paginated wrappers
# ---------------------------------------------------------------------------


class PaginatedProducts(BaseModel):
    """Paginated product listing."""

    total_returned: int
    limit: int
    offset: int
    items: list[ProductListItem]


class PaginatedReviews(BaseModel):
    """Paginated review listing."""

    total_returned: int
    limit: int
    offset: int
    items: list[ReviewListItem]


# ---------------------------------------------------------------------------
# Product Insights
# ---------------------------------------------------------------------------


class RatingBreakdown(BaseModel):
    """Product ratings distribution and averages."""

    model_config = ConfigDict(extra="forbid")

    average_rating: float | None = Field(
        None, description="Average review rating (1.0 to 5.0)."
    )
    total_ratings_count: int = Field(
        0, ge=0, description="Total count of reviews with valid ratings."
    )
    stars_1: int = Field(0, ge=0, description="Count of 1-star ratings.")
    stars_2: int = Field(0, ge=0, description="Count of 2-star ratings.")
    stars_3: int = Field(0, ge=0, description="Count of 3-star ratings.")
    stars_4: int = Field(0, ge=0, description="Count of 4-star ratings.")
    stars_5: int = Field(0, ge=0, description="Count of 5-star ratings.")


class SentimentCounts(BaseModel):
    """Categorical count breakdown of review sentiments."""

    model_config = ConfigDict(extra="forbid")

    positive: int = Field(0, ge=0)
    neutral: int = Field(0, ge=0)
    negative: int = Field(0, ge=0)


class AspectInsight(BaseModel):
    """Aggregated sentiment for a specific product aspect."""

    model_config = ConfigDict(extra="forbid")

    aspect: str
    average_polarity: float = Field(
        ..., ge=-1.0, le=1.0, description="Average aspect compound score [-1.0, 1.0]."
    )
    label: str = Field(..., pattern="^(positive|negative|neutral)$")
    mentions_count: int = Field(0, ge=0)
    snippets: list[str] = Field(default_factory=list)


class TopicInsight(BaseModel):
    """Extracted topic/keyphrase aggregated across reviews."""

    model_config = ConfigDict(extra="forbid")

    term: str
    relevance_score: float = Field(..., ge=0.0)
    frequency: int = Field(..., ge=1)
    ngram_size: int = Field(..., ge=1)


class SentimentInsightSummary(BaseModel):
    """Aggregated sentiment analysis across product reviews."""

    model_config = ConfigDict(extra="forbid")

    average_polarity: float = Field(
        0.0, ge=-1.0, le=1.0, description="Overall average compound score [-1.0, 1.0]."
    )
    sentiment_label: str = Field("neutral", pattern="^(positive|negative|neutral)$")
    counts: SentimentCounts = Field(default_factory=SentimentCounts)
    top_positive_highlights: list[str] = Field(default_factory=list)
    top_negative_highlights: list[str] = Field(default_factory=list)
    aspects: dict[str, AspectInsight] = Field(default_factory=dict)


class ReadabilitySummary(BaseModel):
    """Linguistic readability statistics across reviews."""

    model_config = ConfigDict(extra="forbid")

    average_reading_ease: float | None = Field(
        None, description="Average Flesch Reading Ease score [0-100]."
    )
    consensus_grade_level: float | None = Field(
        None, description="Average consensus US school grade level."
    )
    reading_level_label: str | None = Field(
        None, description="Human-readable reading level interpretation."
    )


class ProductInsightsResponse(BaseModel):
    """Comprehensive analytical insights for a product's reviews."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    product_name: str
    total_reviews_in_db: int = Field(0, ge=0)
    total_reviews_analyzed: int = Field(0, ge=0)
    ratings: RatingBreakdown
    sentiment: SentimentInsightSummary
    top_topics: list[TopicInsight] = Field(default_factory=list)
    readability: ReadabilitySummary


# ---------------------------------------------------------------------------
# On-Demand URL Analysis & Price History
# ---------------------------------------------------------------------------


class PriceSnapshotSchema(BaseModel):
    """A recorded price data point."""

    model_config = ConfigDict(extra="forbid")

    price: float
    original_price: float | None = None
    currency: str = "INR"
    source: str = "unknown"
    observed_at: datetime


class PriceHistoryResponse(BaseModel):
    """Price history summary derived strictly from recorded observations."""

    model_config = ConfigDict(extra="forbid")

    product_id: str
    observations_count: int = Field(0, ge=0)
    first_observed_price: float | None = None
    latest_observed_price: float | None = None
    current_price: float | None = None
    highest_observed_price: float | None = None
    lowest_observed_price: float | None = None
    price_change_amount: float | None = None
    price_change_percentage: float | None = None
    currency: str = "INR"
    is_multi_currency: bool = False
    tracking_start: datetime | None = None
    tracking_end: datetime | None = None
    tracking_period_days: float = Field(0.0, ge=0.0)
    is_historical_peak: bool = False
    status_note: str
    snapshots: list[PriceSnapshotSchema] = Field(default_factory=list)


class AnalyzeUrlRequest(BaseModel):
    """Payload for on-demand product URL analysis."""

    model_config = ConfigDict(extra="forbid")

    url: str = Field(
        ...,
        description="Amazon.in product URL (e.g. 'https://www.amazon.in/dp/B084J4MZK6')",
    )


class ProductUrlAnalysisResponse(BaseModel):
    """Response combining product metadata, observed price history, and NLP insights."""

    model_config = ConfigDict(extra="forbid")

    asin: str
    canonical_url: str
    product: ProductDetailResponse
    price_history: PriceHistoryResponse
    insights: ProductInsightsResponse | None = None
    status_note: str
