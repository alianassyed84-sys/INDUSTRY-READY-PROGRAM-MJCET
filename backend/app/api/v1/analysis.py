"""Linguistic analysis endpoints."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.readability import ReadabilityRequest, ReadabilityResponse
from app.services.readability import calculate_readability

router = APIRouter()


@router.post(
    "/readability",
    response_model=ReadabilityResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze text readability and linguistic complexity",
    description=(
        "Calculates classic English readability metrics (Flesch Reading Ease, "
        "Flesch-Kincaid Grade Level, Gunning Fog Index, Coleman-Liau, and ARI) "
        "alongside structural statistics and reliability assessments."
    ),
)
def audit_readability(payload: ReadabilityRequest) -> ReadabilityResponse:
    """Analyze submitted text and return comprehensive linguistic complexity metrics."""
    report = calculate_readability(payload.text)
    return ReadabilityResponse.model_validate(report.to_dict())
