"""Pydantic schemas for the Language Identifier endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LanguageDetectionRequest(BaseModel):
    """Input payload for language identification."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description="The text content to identify the language of.",
        examples=["ReviewPulse is an AI-powered intelligence platform."],
    )

    @field_validator("text", mode="after")
    @classmethod
    def validate_meaningful_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Text must contain non-whitespace characters.")
        return trimmed


class LanguageCandidateSchema(BaseModel):
    """Individual language candidate score."""

    language_code: str = Field(..., description="ISO 639-1 language code.")
    language_name: str = Field(..., description="Human-readable language name.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0-1.0, higher is better).",
    )
    rank: int = Field(..., ge=1, description="Rank position (1 = best match).")


class LanguageDetectionResponse(BaseModel):
    """Language Identifier response payload."""

    detected_language: str | None = Field(
        None,
        description=(
            "ISO 639-1 code of the detected language, or null if detection "
            "was not possible."
        ),
    )
    detected_language_name: str | None = Field(
        None,
        description="Human-readable name of the detected language, or null.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the top detection result (0.0-1.0).",
    )
    confidence_level: Literal["high", "medium", "low", "unreliable"] = Field(
        ...,
        description="Qualitative confidence classification.",
    )
    is_reliable: bool = Field(
        ...,
        description=(
            "True if the detection confidence is sufficient and the top "
            "candidate is clearly separated from the runner-up."
        ),
    )
    script_fast_path: bool = Field(
        ...,
        description=(
            "True if detection was performed via script analysis (Arabic, "
            "Russian, Chinese, Japanese) rather than full n-gram profiling."
        ),
    )
    candidates: list[LanguageCandidateSchema] = Field(
        default_factory=list,
        description="All evaluated language candidates ranked by confidence.",
    )
    character_count: int = Field(
        ...,
        description="Number of non-whitespace characters in the analyzed text.",
    )
    analyzed_ngrams: int = Field(
        ...,
        description=(
            "Number of distinct n-grams in the input profile used for scoring. "
            "Zero when script fast-path was used."
        ),
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Documented constraints, assumptions, and validity cautions.",
    )
