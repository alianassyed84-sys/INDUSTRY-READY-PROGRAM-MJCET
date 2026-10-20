"""Sentiment analysis endpoint."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status

from app.schemas.sentiment import SentimentRequest, SentimentResponse
from app.services.sentiment import analyze_sentiment

router = APIRouter()


@router.post(
    "/sentiment",
    response_model=SentimentResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze sentiment polarity and aspect-level sentiment for a review",
    description=(
        "Performs rule- and lexicon-based sentiment analysis on a consumer "
        "review text. Calculates compound polarity [-1.0 to +1.0], "
        "positive/negative/neutral proportions, and extracts polar highlight "
        "tokens with negation, booster, and clause modifiers. "
        "Optionally extracts targeted sentiment for specific product aspects."
    ),
)
def evaluate_sentiment(payload: SentimentRequest) -> SentimentResponse:
    """Analyze review sentiment and optional aspect-targeted polarity."""
    result = analyze_sentiment(
        text=payload.text,
        aspects=payload.aspects,
    )
    data = asdict(result)
    return SentimentResponse.model_validate(data)
