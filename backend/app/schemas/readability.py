"""Pydantic schemas for the Readability Auditor endpoint."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReadabilityRequest(BaseModel):
    """Input payload for linguistic complexity and readability analysis."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=100_000,
        description=(
            "The text content to analyze for readability and linguistic complexity."
        ),
        examples=[
            "ReviewPulse is an AI-powered intelligence platform that analyzes customer "
            "reviews with speed and precision."
        ],
    )

    @field_validator("text", mode="after")
    @classmethod
    def validate_meaningful_content(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("Text must contain non-whitespace characters.")
        return trimmed


class TextStatisticsSchema(BaseModel):
    """Descriptive structural statistics of the text."""

    character_count: int = Field(..., description="Count of non-whitespace characters.")
    letter_count: int = Field(..., description="Count of alphabetical letters.")
    word_count: int = Field(..., description="Count of recognizable linguistic words.")
    sentence_count: int = Field(..., description="Count of segmented sentences.")
    syllable_count: int = Field(..., description="Estimated count of syllables.")
    complex_word_count: int = Field(
        ..., description="Count of words with 3 or more syllables."
    )
    unique_word_count: int = Field(
        ..., description="Count of distinct vocabulary words."
    )
    avg_words_per_sentence: float = Field(
        ..., description="Average words per sentence."
    )
    avg_syllables_per_word: float = Field(
        ..., description="Average syllables per word."
    )
    avg_letters_per_word: float = Field(..., description="Average letters per word.")
    complex_word_percentage: float = Field(
        ..., description="Percentage of words that are complex."
    )
    type_token_ratio: float = Field(
        ..., description="Lexical diversity ratio (unique words / total words)."
    )


class ReadabilityScoreSchema(BaseModel):
    """Detailed score result for an individual readability metric."""

    score: float | None = Field(
        None,
        description=(
            "Calculated numerical formula score, or null if text is too short "
            "for reliable calculation."
        ),
    )
    grade_level: float | None = Field(
        None,
        description="Equivalent US school grade level, or null if uncalculated.",
    )
    interpretation: str | None = Field(
        None,
        description="Qualitative educational or reading comprehension level.",
    )
    description: str = Field(
        ..., description="Methodology and interpretation note for this formula."
    )


class ReadabilityResponse(BaseModel):
    """Comprehensive Readability Auditor response payload."""

    is_analyzable: bool = Field(
        ...,
        description=(
            "True if text contains sufficient linguistic tokens for "
            "statistical scoring."
        ),
    )
    reliability: Literal["high", "medium", "low", "unreliable"] = Field(
        ...,
        description="Confidence classification based on sample size and token count.",
    )
    language: str = Field("en", description="Target language standard (default: en).")
    statistics: TextStatisticsSchema = Field(
        ..., description="Text structure and length counts."
    )
    flesch_reading_ease: ReadabilityScoreSchema = Field(
        ..., description="Flesch Reading Ease (0-100 scale)."
    )
    flesch_kincaid_grade: ReadabilityScoreSchema = Field(
        ..., description="Flesch-Kincaid Grade Level."
    )
    gunning_fog: ReadabilityScoreSchema = Field(..., description="Gunning Fog Index.")
    coleman_liau: ReadabilityScoreSchema = Field(..., description="Coleman-Liau Index.")
    automated_readability_index: ReadabilityScoreSchema = Field(
        ..., description="Automated Readability Index."
    )
    consensus_grade_level: float | None = Field(
        None,
        description=(
            "Consensus average grade level computed across all four "
            "grade-level formulas."
        ),
    )
    reading_time_seconds: float = Field(
        ...,
        description="Estimated reading time in seconds assuming 200 words per minute.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description=(
            "Documented constraints, assumptions, and validity cautions "
            "for this evaluation."
        ),
    )
