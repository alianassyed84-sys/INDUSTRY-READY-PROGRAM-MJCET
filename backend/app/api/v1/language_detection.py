"""Language identification endpoint."""

from __future__ import annotations

from fastapi import APIRouter, status

from app.schemas.language_detection import (
    LanguageDetectionRequest,
    LanguageDetectionResponse,
)
from app.services.language_detection import detect_language

router = APIRouter()


@router.post(
    "/language",
    response_model=LanguageDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Identify the language of submitted text",
    description=(
        "Uses character n-gram rank-order profiling (Cavnar & Trenkle, 1994) "
        "to estimate the most likely language of the input text. "
        "Supports: English, German, French, Spanish, Italian, Portuguese, "
        "Dutch, Polish, Russian, Arabic, Chinese, and Japanese."
    ),
)
def identify_language(payload: LanguageDetectionRequest) -> LanguageDetectionResponse:
    """Analyze submitted text and return ranked language detection results."""
    from dataclasses import asdict

    result = detect_language(payload.text)
    return LanguageDetectionResponse.model_validate(asdict(result))
